import chainlit as cl


@cl.on_chat_start
async def on_start():
    await cl.Message("Hello world from Fly.io!").send()


@cl.on_message
async def on_message(message: cl.Message):
    await cl.Message(
        f"Received message: {message.content}. This demo is all about deploying your Chainlit app on Fly.io, nothing else!"
    ).send()
