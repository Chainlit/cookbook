import json
import ast
import os
import asyncio
from openai import AsyncOpenAI

from chainlit.playground.providers.openai import stringify_function_call
import chainlit as cl

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

MAX_ITER = 5

def get_current_weather(location, unit):
    unit = unit or "Farenheit"
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }

    return json.dumps(weather_info)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

@cl.step(type="tool")
async def call_tool(tool_call, location):
    function_name = tool_call.function.name
    arguments = {"location": location}

    current_step = cl.context.current_step
    current_step.name = function_name

    current_step.input = arguments

    function_response = get_current_weather(
        location=arguments.get("location"),
        unit=arguments.get("unit"),
    )

    current_step.output = function_response
    current_step.language = "json"

    return {
        "role": "function",
        "name": function_name,
        "content": function_response,
        "tool_call_id": tool_call.id,
    }

@cl.step(type="llm")
async def call_gpt4(message_history):
    settings = {
        "model": "gpt-4",
        "tools": tools,
        "tool_choice": "auto",
    }

    cl.context.current_step.generation = cl.ChatGeneration(
        provider="openai-chat",
        messages=[
            cl.GenerationMessage(
                formatted=m["content"], name=m.get("name"), role=m["role"]
            )
            for m in message_history
        ],
        settings=settings,
    )

    response = await client.chat.completions.create(
        messages=message_history, **settings
    )

    message = response.choices[0].message

    # Parse locations from message content
    locations = message.content.split(" and ")

    # Call get_current_weather for each location
    tasks = [call_tool(tool_call, location.strip()) for location in locations for tool_call in message.tool_calls or [] if tool_call.type == "function"]
    await asyncio.gather(*tasks)

    if message.content:
        cl.context.current_step.generation.completion = message.content
        cl.context.current_step.output = message.content

    elif message.tool_calls:
        completion = stringify_function_call(message.tool_calls[0].function)

        cl.context.current_step.generation.completion = completion
        cl.context.current_step.language = "json"
        cl.context.current_step.output = completion

    return message

@cl.on_message
async def run_conversation(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        # Create a list of tasks for each message in the message history
        tasks = [call_gpt4(message) for message in message_history]

        # Run tasks concurrently using asyncio.gather
        messages = await asyncio.gather(*tasks)

        # Process the returned messages
        for message in messages:
            if not message.tool_calls:
                await cl.Message(content=message.content, author="Answer").send()
                break

        cur_iter += 1