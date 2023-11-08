import json
import ast
import os
from openai import AsyncOpenAI

import chainlit as cl
from chainlit.prompt import Prompt, PromptMessage

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

MAX_ITER = 5


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit):
    """Get the current weather in a given location"""
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


@cl.on_message
async def run_conversation(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        settings = {
            "model": "gpt-4",
            "tools": tools,
            "tool_choice": "auto",
        }

        prompt = Prompt(
            provider="openai-chat",
            messages=[
                PromptMessage(
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

        prompt.completion = message.content or ""

        root_msg_id = await cl.Message(
            prompt=prompt, author=message.role, content=prompt.completion
        ).send()

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            if tool_call.type == "function":
                function_name = tool_call.function.name
                arguments = ast.literal_eval(tool_call.function.arguments)
                await cl.Message(
                    author=function_name,
                    content=str(tool_call.function),
                    language="json",
                    parent_id=root_msg_id,
                ).send()

                function_response = get_current_weather(
                    location=arguments.get("location"),
                    unit=arguments.get("unit"),
                )

                message_history.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                        "tool_call_id": tool_call.id,
                    }
                )

                await cl.Message(
                    author=function_name,
                    content=str(function_response),
                    language="json",
                    parent_id=root_msg_id,
                ).send()
        cur_iter += 1
