import chainlit as cl


@cl.on_chat_start
def on_start():
    cl.Message("Hello world from Fly.io!").send()


@cl.on_message
def on_message(message):
    cl.Message(
        f"Received message: {message}. This demo is all about deploying your Chainlit app on Fly.io, nothing else!"
    ).send()
