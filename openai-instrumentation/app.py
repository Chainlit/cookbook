from openai import AsyncOpenAI

from chainlit.playground.providers import ChatOpenAI
import chainlit as cl

client = AsyncOpenAI()
cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    # ... more settings
}

# @cl.step(type="llm")
async def call_llm(input):
    response = await client.chat.completions.create(
        messages=[
            cl.GenerationMessage(
                content="You are a helpful bot, you always reply in Spanish", role="system"
            ),
            cl.GenerationMessage(
                content=input, role="user"
            ),
        ],
        **settings
    )

    return response.choices[0].message.content


@cl.on_message
async def on_message(message: cl.Message):
    response = await call_llm(message.content)
    await cl.Message(content=response).send()

# @cl.on_chat_start
# async def on_chat_start():
#     response = await call_llm("What is the weather like in San Francisco?")
#     await cl.Message(content=response).send()
