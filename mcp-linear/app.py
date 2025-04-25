import json

from mcp import ClientSession
import anthropic

import chainlit as cl

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

anthropic_client = anthropic.AsyncAnthropic()
SYSTEM = "You are a helpful assistant. You are a member of a team that uses Linear to manage their projects. Once you've diplayed a ticket, do not mention it again in your response - JUST SAY `here is the ticket information!`"
regular_tools = [
    {
        "name": "show_linear_ticket",
        "description": "Displays a Linear ticket in the UI with its details. Use this tool after retrieving ticket information to show a visual representation of the ticket. The tool will create a card showing the ticket title, status, assignee, deadline, and tags. This provides a cleaner presentation than text-only responses.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "status": {"type": "string"},
                "assignee": {"type": "string"},
                "deadline": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "status", "assignee", "deadline", "tags"],
        },
    }
]


async def show_linear_ticket(title, status, assignee, deadline, tags):
    props = {
        "title": title,
        "status": status,
        "assignee": assignee,
        "deadline": deadline,
        "tags": tags,
    }
    print("props", props)
    ticket_element = cl.CustomElement(name="LinearTicket", props=props)
    await cl.Message(
        content="", elements=[ticket_element], author="show_linear_ticket"
    ).send()
    return "the ticket was displayed to the user: " + str(props)


def flatten(xss):
    return [x for xs in xss for x in xs]


@cl.on_mcp_connect
async def on_mcp(connection, session: ClientSession):
    result = await session.list_tools()
    tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
        } for t in result.tools]
    
    # Save tools to a JSON file
    import os
    
    # Create directory if it doesn't exist
    os.makedirs("tools_data", exist_ok=True)
    
    # Save to JSON file
    with open(f"tools_data/{connection.name}_tools.json", "w") as f:
        json.dump(tools, f, indent=2)
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection.name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)


@cl.step(type="tool")
async def call_tool(tool_use):
    tool_name = tool_use.name
    tool_input = tool_use.input

    current_step = cl.context.current_step
    current_step.name = tool_name

    # Identify which mcp is used
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_name = None

    for connection_name, tools in mcp_tools.items():
        if any(tool.get("name") == tool_name for tool in tools):
            mcp_name = connection_name
            break

    if not mcp_name:
        current_step.output = json.dumps(
            {"error": f"Tool {tool_name} not found in any MCP connection"}
        )
        return current_step.output

    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)

    if not mcp_session:
        current_step.output = json.dumps(
            {"error": f"MCP {mcp_name} not found in any MCP connection"}
        )
        return current_step.output

    try:
        current_step.output = await mcp_session.call_tool(tool_name, tool_input)
    except Exception as e:
        current_step.output = json.dumps({"error": str(e)})

    return current_step.output


async def call_claude(chat_messages):
    msg = cl.Message(content="")
    mcp_tools = cl.user_session.get("mcp_tools", {})
    regular_tools = cl.user_session.get("regular_tools", [])
    # Flatten the tools from all MCP connections
    tools = flatten([tools for _, tools in mcp_tools.items()]) + regular_tools
    print([tool.get("name") for tool in tools])
    async with anthropic_client.messages.stream(
        system=SYSTEM,
        max_tokens=1024,
        messages=chat_messages,
        tools=tools,
        model="claude-3-5-sonnet-20240620",
    ) as stream:
        async for text in stream.text_stream:
            await msg.stream_token(text)

    await msg.send()
    response = await stream.get_final_message()

    return response


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("chat_messages", [])
    cl.user_session.set("regular_tools", regular_tools)


@cl.on_message
async def on_message(msg: cl.Message):
    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "user", "content": msg.content})
    response = await call_claude(chat_messages)

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")
        if tool_use.name == "show_linear_ticket":
            tool_result = await show_linear_ticket(**tool_use.input)
        else:
            tool_result = await call_tool(tool_use)

        messages = [
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(tool_result),
                    }
                ],
            },
        ]

        chat_messages.extend(messages)
        response = await call_claude(chat_messages)

    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )

    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "assistant", "content": final_response})
