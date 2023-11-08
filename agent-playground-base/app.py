from openai import AsyncOpenAI
import chainlit as cl
from chainlit.prompt import Prompt, PromptMessage
from chainlit.playground.providers import ChatOpenAI

client = AsyncOpenAI()

template = "Hello, {name}!"
inputs = {"name": "John"}

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0,
    # ... more settings
}


@cl.on_chat_start
async def start():
    # Create the Chainlit Prompt instance
    prompt = Prompt(
        provider=ChatOpenAI.id,
        inputs=inputs,
        settings=settings,
        messages=[
            PromptMessage(
                template=template, formatted=template.format(**inputs), role="assistant"
            )
        ],
    )

    # Make the call to OpenAI
    response = await client.chat.completions.create(
        messages=[m.to_openai() for m in prompt.messages], **settings
    )

    prompt.completion = response.choices[0].message.content

    await cl.Message(
        content="The content of the message is not important.",
        prompt=prompt,
    ).send()
