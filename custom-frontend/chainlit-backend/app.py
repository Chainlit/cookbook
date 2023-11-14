import chainlit as cl


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Connected to Chainlit!").send()
    
    
@cl.on_message
async def on_message(message: cl.Message):
    await cl.Message(content=f"Received: {message.content}").send()