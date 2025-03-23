import os
import anthropic
import chainlit as cl

c = anthropic.AsyncAnthropic()


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("messages", [])


async def call_claude(query: str):
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": query})

    msg = cl.Message(content="", author="Claude")

    stream = await c.messages.create(
        model="claude-3-5-sonnet-latest",
        messages=messages,
        max_tokens=1000,
        stream=True,
    )

    async for data in stream:
        if data.type == "content_block_delta":
            await msg.stream_token(data.delta.text)

    await msg.send()
    messages.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("messages", messages)


@cl.on_message
async def chat(message: cl.Message):
    await call_claude(message.content)
