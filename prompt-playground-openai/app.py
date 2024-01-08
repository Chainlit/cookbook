from openai import AsyncOpenAI
import chainlit as cl
from chainlit.playground.providers import ChatOpenAI

client = AsyncOpenAI()

template = "Hello, {name}!"
inputs = {"name": "John"}

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    # ... more settings
}


@cl.step(name="gpt-3.5", type="llm")
async def call_openai():
    generation = cl.ChatGeneration(
        provider=ChatOpenAI.id,
        inputs=inputs,
        settings=settings,
        messages=[
            cl.GenerationMessage(
                template=template, formatted=template.format(**inputs), role="assistant"
            )
        ],
    )

    # Make the call to OpenAI
    response = await client.chat.completions.create(
        messages=[m.to_openai() for m in generation.messages], **settings
    )

    generation.completion = response.choices[0].message.content

    cl.context.current_step.generation = generation

    return generation.completion


@cl.on_chat_start
async def start():
    await call_openai()
