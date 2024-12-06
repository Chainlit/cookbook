from openai import AsyncOpenAI

from chainlit.playground.providers import ChatOpenAI
import chainlit as cl

client = AsyncOpenAI()

# Instrument the OpenAI client
cl.instrument_openai()

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    # ... more settings
}

async def call_llm(input):
    response = await client.chat.completions.create(
        messages=[
            {
                "content": "You are a helpful bot, you always reply in Spanish",
                "role": "system"
            },
            {
                "content": input,
                "role": "user"
            }
        ],
        **settings
    )

    return response.choices[0].message.content


@cl.on_message
async def on_message(message: cl.Message):
    response = await call_llm(message.content)
    await cl.Message(content=response).send()

