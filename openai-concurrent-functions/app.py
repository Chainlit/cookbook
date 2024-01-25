from openai import AsyncOpenAI
import json, os, asyncio
import chainlit as cl

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
@cl.step(type="tool", show_input="json", language="json")
async def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

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
    # Step 1: send the conversation and available functions to the model
    
    msg = cl.Message(author="Assistant", content="")
    await msg.send()

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=message_history,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    
    msg.content = response_message.content or ""
    await msg.update()

    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        message_history.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        async def call_function(tool_call):
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = await function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }

        # Use asyncio.gather to make function calls in parallel
        function_responses = await asyncio.gather(
            *(call_function(tool_call) for tool_call in tool_calls)
        )

        # Extend conversation with all function responses
        message_history.extend(function_responses)
        second_response = await client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=message_history,
        )  # get a new response from the model where it can see the function response
        second_message = second_response.choices[0].message
        await cl.Message(author="Assistant", content=second_message.content).send()