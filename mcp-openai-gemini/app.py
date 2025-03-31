import json
import os
import chainlit as cl
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession 

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta"
)

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
SYSTEM = "you are a helpful assistant."

def flatten(xss):
    """Flattens a list of lists into a single list."""
    return [x for xs in xss for x in xs]

def handle_tool_error(current_step, error_msg):
    """Helper function to handle tool errors consistently"""
    current_step.output = json.dumps({"error": error_msg})
    current_step.is_error = True
    return json.dumps({"error": error_msg})

def find_mcp_connection_for_tool(tool_name, mcp_tools_by_connection):
    """Find which MCP connection contains the requested tool"""
    for conn_name, tools_metadata in mcp_tools_by_connection.items():
        if any(tool_meta["name"] == tool_name for tool_meta in tools_metadata):
            return conn_name
    return None

@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """
    Called when a user connects to an MCP server.
    Discovers tools and stores their metadata.
    """
    try:
        result = await session.list_tools()
        
        tools_metadata = [{
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema, 
            "mcp_connection_name": connection.name
        } for t in result.tools]
        
        mcp_tools = cl.user_session.get("mcp_tools", {})
        mcp_tools[connection.name] = tools_metadata
        cl.user_session.set("mcp_tools", mcp_tools)

    except Exception as e:
        await cl.ErrorMessage(f"Failed to list tools from MCP server '{connection.name}': {e}").send()

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    """
    Called when an MCP connection is closed. Removes associated tools.
    """
    mcp_tools = cl.user_session.get("mcp_tools", {})
    if name in mcp_tools:
        del mcp_tools[name]
        cl.user_session.set("mcp_tools", mcp_tools)

@cl.step(type="tool")
async def call_mcp_tool(tool_call):
    """
    Executes a specific tool call requested by the LLM via the correct MCP session.
    Updates the Chainlit UI step with execution details.
    """
    tool_name = tool_call.function.name
    current_step = cl.context.current_step
    current_step.name = tool_name 

    try:
        tool_input = json.loads(tool_call.function.arguments)
        current_step.input = tool_input 
    except json.JSONDecodeError:
        return handle_tool_error(
            current_step,
            f"Error: Invalid JSON arguments received for tool {tool_name}: {tool_call.function.arguments}"
        )
    
    mcp_tools_by_connection = cl.user_session.get("mcp_tools", {})
    mcp_connection_name = find_mcp_connection_for_tool(tool_name, mcp_tools_by_connection)

    if not mcp_connection_name:
        return handle_tool_error(
            current_step,
            f"Tool '{tool_name}' not found in any active MCP connection."
        )

    mcp_session_tuple = cl.context.session.mcp_sessions.get(mcp_connection_name)
    if not mcp_session_tuple:
        return handle_tool_error(
            current_step,
            f"Active MCP session for connection '{mcp_connection_name}' not found."
        )

    mcp_session: ClientSession = mcp_session_tuple[0] 
    
    try:
        result = await mcp_session.call_tool(tool_name, arguments=tool_input)
        
        if isinstance(result, (dict, list)):
           current_step.output = json.dumps(result, indent=2)
        else:
           current_step.output = str(result)
        
        return str(result)

    except Exception as e:
        return handle_tool_error(
            current_step,
            f"Error executing MCP tool '{tool_name}': {e}"
        )

def format_mcp_tools_for_openai(mcp_tools_by_connection):
    """
    Converts stored MCP tool metadata into the OpenAI API 'tools' format.
    """
    all_mcp_tools = flatten(list(mcp_tools_by_connection.values()))
    return [{
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"] 
        }
    } for tool in all_mcp_tools]

async def call_llm(chat_messages):
    """
    Calls the LLM model via the OpenAI SDK, handles streaming, and tool calls.
    Uses a non-streaming call at the end to reliably get tool call details.
    """
    msg = cl.Message(content="")
    await msg.send() 

    mcp_tools_by_connection = cl.user_session.get("mcp_tools", {})
    tools_for_openai = format_mcp_tools_for_openai(mcp_tools_by_connection)

    try:
        api_args = {
            "model": MODEL_NAME,
            "messages": chat_messages,
            "temperature": 0.5,
        }
        if tools_for_openai:
            api_args["tools"] = tools_for_openai
            api_args["tool_choice"] = "auto"

        stream_resp = await client.chat.completions.create(**{**api_args, "stream": True})

        async for chunk in stream_resp:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                await msg.stream_token(delta.content)

        await msg.update() 
        
        final_response = await client.chat.completions.create(**{**api_args, "stream": False})
        assistant_message = final_response.choices[0].message
        
        return assistant_message 

    except Exception as e:
        return None 

@cl.on_chat_start
async def start_chat():
    """Initializes chat history and MCP tool storage on new chat session."""
    cl.user_session.set("chat_messages", [{"role": "system", "content": SYSTEM}])
    cl.user_session.set("mcp_tools", {}) 

async def process_tool_calls(assistant_response_message):
    """Process tool calls from the assistant response"""
    tool_messages_for_llm = []
    for tool_call in assistant_response_message.tool_calls:
        if tool_call.type == "function":
            tool_result_content = await call_mcp_tool(tool_call) 
            tool_messages_for_llm.append({
                "role": "tool",
                "tool_call_id": tool_call.id, 
                "content": tool_result_content, 
            })
        else:
            tool_messages_for_llm.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps({"error": f"Unsupported tool type: {tool_call.type}"}),
            })
    return tool_messages_for_llm

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming user messages, orchestrates LLM calls and tool execution loop.
    """
    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "user", "content": message.content})
    
    while True:
        assistant_response_message = await call_llm(chat_messages)

        if not assistant_response_message:
            await cl.ErrorMessage("Assistant failed to generate a response.").send()
            return
        
        chat_messages.append(assistant_response_message.model_dump(exclude_unset=True))
        
        if not assistant_response_message.tool_calls:
            break 
        
        tool_messages = await process_tool_calls(assistant_response_message)
        
        chat_messages.extend(tool_messages)
    
    cl.user_session.set("chat_messages", chat_messages)