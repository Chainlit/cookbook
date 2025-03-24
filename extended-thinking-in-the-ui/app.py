import chainlit as cl
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = Anthropic()

@cl.on_chat_start
async def start():
    cl.user_session.set("message_history", [])

@cl.step(name="Extended Thinking", show_input=False)
async def thinking_step(user_message: str):
    current_step = cl.context.current_step
    current_step.output = ""
    has_thinking = False
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model="claude-3-7-sonnet-latest",
        system="You are a helpful assistant! Your goal is to provide the most accurate and truthful responses possible. ",
        max_tokens=64000,
        thinking={"type": "enabled", "budget_tokens": 20000},
        messages=message_history,
        stream=True
    )
    for chunk in response:
        if chunk.type == "content_block_delta" and chunk.index == 0:
            delta = chunk.delta
            if getattr(delta, "type", None) == "thinking_delta" and hasattr(delta, "thinking"):
                await current_step.stream_token(delta.thinking)
                has_thinking = True
        elif chunk.type == "content_block_stop" and chunk.index == 0:
            break
    return has_thinking, response

@cl.on_message
async def main(msg: cl.Message):
    message_history = cl.user_session.get("message_history")
    has_thinking, response = await thinking_step(msg.content)
    final_message = cl.Message(content="")
    await final_message.send()
    ai_response = ""
    for chunk in response:
        if has_thinking and chunk.type == "content_block_delta" and chunk.index == 0:
            continue
        elif chunk.type == "content_block_delta" and chunk.index == 1:
            delta = chunk.delta
            if getattr(delta, "type", None) == "text_delta" and hasattr(delta, "text"):
                await final_message.stream_token(delta.text)
                ai_response += delta.text
        elif chunk.type == "content_block_stop" and chunk.index == 1:
            await final_message.update()
    if ai_response:
        message_history.append({"role": "assistant", "content": ai_response})
        cl.user_session.set("message_history", message_history)