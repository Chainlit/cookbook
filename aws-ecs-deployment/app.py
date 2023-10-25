import chainlit as cl


@cl.on_chat_start
async def on_start():
    await cl.Message("Hello world from AWS!").send()


@cl.on_message
async def on_message(message: cl.Message):
    await cl.Message(
        f"Received message: {message.content}. This demo is all about deploying your Chainlit app on AWS ECS, nothing else!"
    ).send()