import json
import ast
import os
from typing import Any
from openai import AsyncOpenAI

from chainlit.playground.providers import ChatOpenAI
from chainlit.playground.providers.openai import stringify_function_call
import chainlit as cl
from chainlit.input_widget import Select, Slider


open_ai_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
AVATAR = cl.Avatar(
        name="ChatGPT",
        url="https://github.com/ndamulelonemakh/remote-assets/blob/7ed514dbd99ab86536daf3942127822bd979936c/images/openai-logomark.png?raw=true",
)
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

chat_settings = {
        "model": "gpt-4",
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 1000,
        "temperature": 0.2
}
user_setttings = [
    Select(
        id="model",
        label="Model",
        values=["gpt-4-turbo", "gpt-3.5-turbo-0125"],
        initial_index=0,
    ),
    Slider(
                id="temperature",
                label="Temperature",
                initial=0.2,
                min=0,
                max=1,
                step=0.1,
            ),
    Slider(
                id="max_tokens",
                label="Maxiumum Completions Tokens",
                initial=1000,
                min=100,
                max=32000,
                step=10,
                description="The maximum allowable tokens in the response",
    ),
    
]
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


@cl.step(type="tool")
async def call_tool(tool_call, message_history):
    function_name = tool_call.function.name
    arguments = ast.literal_eval(tool_call.function.arguments)

    current_step = cl.context.current_step
    current_step.name = function_name

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
            "name": function_name,
            "content": function_response,
            "tool_call_id": tool_call.id,
        }
    )


@cl.step(name="ChatGPT-Completions", type="llm")
async def _get_chat_completions(message_history: list[dict], settings: dict[str, Any] = None):
    settings = settings or chat_settings
    if "max_tokens" in settings:
        settings["max_tokens"] = int(settings["max_tokens"])
        
    response = await open_ai_client.chat.completions.create(
        messages=message_history, **settings
    )

    message = response.choices[0].message
    for tool_call in message.tool_calls or []:
        if tool_call.type == "function":
            await call_tool(tool_call, message_history)

    if message.content:
        cl.context.current_step.output = message.content

    elif message.tool_calls:
        completion = stringify_function_call(message.tool_calls[0].function)

        cl.context.current_step.language = "json"
        cl.context.current_step.output = completion

    return message


@cl.step(name="ChatGPT", 
         type="llm", 
         root=True)
async def call_chatgpt_with_tools(query: str, settings: dict[str, Any] = None):
    message_history = cl.user_session.get("prompt_history")
    message_history.append({"name": "user", "role": "user", "content": query})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        response_message = await _get_chat_completions(message_history, settings=settings)
        if not response_message.tool_calls:
            await cl.Message(content=response_message.content, author="Answer").send()
            break

        cur_iter += 1
        
        
        
@cl.step(name="ChatGPT", 
         type="llm", 
         root=True)
async def call_chatgpt(query: str, settings: dict[str, Any] = chat_settings):
    message_history = cl.user_session.get("prompt_history")
    message_history.append({"name": "User", "role": "user", "content": query})


    if "max_tokens" in settings:
        settings["max_tokens"] = int(settings["max_tokens"])
        
    stream = await open_ai_client.chat.completions.create(
        messages=message_history, 
        stream=True,
        **settings
    )
    
    async for part in stream:
        token = part.choices[0].delta.content
        if token:
            await cl.context.current_step.stream_token(token)
        
    
    cl.context.current_step.generation = cl.CompletionGeneration(
        formatted=query,
        completion=cl.context.current_step.output,
        settings=settings,
        provider=ChatOpenAI.id,
    )

    message_history.append({"name": "ChatGPT", 
                            "role": "assistant", 
                            "content": cl.context.current_step.output})
    cl.user_session.set("prompt_history", message_history)
    
