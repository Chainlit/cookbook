import chainlit as cl
import json
from anthropic import AsyncAnthropic
SYSTEM = "you are a helpful assistant."
MODEL_NAME = "claude-3-5-sonnet-20240620"
c = AsyncAnthropic()

# hard coded weather tool
async def get_current_weather(location, unit):
    """Get the current weather in a given location"""
    unit = unit or "Farenheit"
    weather_info = {
        "location": location,
        "temperature": "74",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }

    return json.dumps(weather_info)

# simple calculator tool
async def calculator(operation, operand1, operand2):
    """Perform a basic arithmetic operation"""
    result = None
    
    if operation == "add":
        result = operand1 + operand2
    elif operation == "subtract":
        result = operand1 - operand2
    elif operation == "multiply":
        result = operand1 * operand2
    elif operation == "divide":
        if operand2 != 0:
            result = operand1 / operand2
        else:
            return json.dumps({"error": "Division by zero is not allowed"})
    else:
        return json.dumps({"error": "Invalid operation"})

    calculation_info = {
        "operation": operation,
        "operand1": operand1,
        "operand2": operand2,
        "result": result
    }
    
    return json.dumps(calculation_info)

# tool descriptions
tools = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather for a specified location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. 'San Francisco, CA'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature to use (celsius or fahrenheit)"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "calculator",
        "description": "A simple calculator that performs basic arithmetic operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform."
                },
                "operand1": {
                    "type": "number",
                    "description": "The first operand."
                },
                "operand2": {
                    "type": "number",
                    "description": "The second operand."
                }
            },
            "required": ["operation", "operand1", "operand2"]
        }
    }
]

# tool mappings
TOOL_FUNCTIONS = {
    "get_current_weather": get_current_weather,
    "calculator": calculator
}

# send chat messages to claude api
async def call_claude(chat_messages):
    msg = cl.Message(content="", author="Claude")

    async with c.messages.stream(
        max_tokens=1024,
        system=SYSTEM,
        messages=chat_messages,
        tools=tools,
        model="claude-3-5-sonnet-20240620",
    ) as stream:
        async for text in stream.text_stream:
            await msg.stream_token(text)
    
    await msg.send()
    response = await stream.get_final_message()

    return response

# initialise chat
@cl.on_chat_start
async def start_chat():
    cl.user_session.set("chat_messages", [])

# route to functions based on tool call
@cl.step(type="tool") 
async def call_tool(tool_use):
    tool_name = tool_use.name
    tool_input = tool_use.input
    
    current_step = cl.context.current_step
    current_step.name = tool_name
    
    tool_function = TOOL_FUNCTIONS.get(tool_name)
    
    if tool_function:
        try:
            current_step.output = await tool_function(**tool_input)
        except TypeError:
            current_step.output = json.dumps({"error": f"Invalid input for {tool_name}"})
    else:
        current_step.output = json.dumps({"error": f"Invalid tool: {tool_name}"})
    
    current_step.language = "json"
    return current_step.output

# main chat
@cl.on_message
async def chat(message: cl.Message):
    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "user", "content": message.content})
    response = await call_claude(chat_messages)

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")
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