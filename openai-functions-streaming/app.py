import json
import ast
import os
from openai import AsyncOpenAI

import chainlit as cl
from chainlit.playground.providers.openai import stringify_function_call

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

MAX_ITER = 5


def get_current_weather(location, unit):
    unit = unit or "Fahrenheit"
    weather_info = {
        "location": location,
        "temperature": "60",
        "unit": unit,
        "forecast": ["windy"],
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
async def call_tool(tool_call_id, name, arguments, message_history):
    arguments = ast.literal_eval(arguments)

    current_step = cl.context.current_step
    current_step.name = name
    current_step.input = arguments

    function_response = get_current_weather(
        location=arguments.get("location"),
        unit=arguments.get("unit"),
    )

    current_step.output = function_response
    current_step.language = "json"

    message_history.append(
        {
            "role": "function",
            "name": name,
            "content": function_response,
            "tool_call_id": tool_call_id,
        }
    )


@cl.step(type="llm")
async def call_gpt4(message_history):
    settings = {
        "model": "gpt-3.5-turbo",
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0,
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

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    tool_call_id = None
    function_output = {"name": "", "arguments": ""}

    final_answer = cl.Message(content="", author="Answer")

    async for part in stream:
        new_delta = part.choices[0].delta
        tool_call = new_delta.tool_calls and new_delta.tool_calls[0]
        function = tool_call and tool_call.function
        if tool_call and tool_call.id:
            tool_call_id = tool_call.id

        if function:
            if function.name:
                function_output["name"] = function.name
            else:
                function_output["arguments"] += function.arguments
            await cl.context.current_step.stream_token(
                json.dumps(function_output), is_sequence=True
            )
        if new_delta.content:
            await cl.context.current_step.stream_token(new_delta.content)
            if not final_answer.content:
                await final_answer.send()
            await final_answer.stream_token(new_delta.content)

    cl.context.current_step.generation.completion = cl.context.current_step.output

    if tool_call_id:
        cl.context.current_step.output = stringify_function_call(function_output)
        cl.context.current_step.language = "json"
        await call_tool(
            tool_call_id,
            function_output["name"],
            function_output["arguments"],
            message_history,
        )

    if final_answer.content:
        await final_answer.update()

    return tool_call_id


@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        tool_call_id = await call_gpt4(message_history)
        if not tool_call_id:
            break

        cur_iter += 1
