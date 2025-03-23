import chainlit as cl

# WARNING: You need to clear your browser cache to see the new logo and favicon.


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="We are Pied Piper!").send()
