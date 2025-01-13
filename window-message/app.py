import chainlit as cl

@cl.on_window_message
async def window_message(message: str):
    if message.startswith("Client: "):
        await cl.Message(content=f"Window message received: {message}").send()
        await cl.send_window_message(f"Server: Window message received: {message}")

@cl.on_message
async def on_message(msg: cl.Message):
    await cl.Message(content=f"Normal message received: {msg.content}").send()
    await cl.send_window_message(f"Server: Normal message received: {msg.content}")
