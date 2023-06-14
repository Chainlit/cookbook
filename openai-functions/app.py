import openai
import json
import os
import chainlit as cl

openai.api_key = os.environ.get("OPENAI_API_KEY")

MAX_ITER = 5


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


functions = [
    {
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
    }
]


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def run_conversation(user_message: str):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": user_message})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages=message_history,
            functions=functions,
            function_call="auto",
        )

        message = response["choices"][0]["message"]
        await cl.Message(author=message["role"], content=message["content"]).send()
        message_history.append(message)

        if not message.get("function_call"):
            break

        function_name = message["function_call"]["name"]
        await cl.Message(
            author=function_name,
            content=str(message["function_call"]),
            language="json",
            indent=1,
        ).send()

        function_response = get_current_weather(
            location=message.get("location"),
            unit=message.get("unit"),
        )

        message_history.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )

        await cl.Message(
            author=function_name,
            content=str(function_response),
            language="json",
            indent=1,
        ).send()
        cur_iter += 1
