import chainlit as cl


@cl.on_message
async def on_message(msg: cl.Message):
    return cl.Message(content="Hello, world!")
