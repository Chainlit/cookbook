from dotenv import load_dotenv
load_dotenv()


import os
from openai import AsyncOpenAI
import chainlit as cl

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)
cl.instrument_openai()

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

@cl.step(type="run")
async def call_gpt4(message_history):
    settings = {
        "model": "gpt-4",
    }

    response = await client.chat.completions.create(
        messages=message_history, **settings
    )

    return response.choices[0].message


@cl.on_message
async def run_conversation(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    message = await call_gpt4(message_history)
    message_history.append({"role": "assistant", "content": message.content})
    await cl.Message(content=message.content, author="Answer").send()
