import os
import anthropic
import chainlit as cl

c = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "prompt_history",
        "",
    )


async def call_claude(query: str):
    prompt_history = cl.user_session.get("prompt_history")

    prompt = f"{prompt_history}{anthropic.HUMAN_PROMPT}{query}{anthropic.AI_PROMPT}"

    settings = {
        "stop_sequences": [anthropic.HUMAN_PROMPT],
        "max_tokens_to_sample": 1000,
        "model": "claude-2.0",
    }
    
    msg = cl.Message(content="", author="Claude")

    stream = await c.completions.create(
        prompt=prompt,
        stream=True,
        **settings,
    )

    async for data in stream:
        token = data.completion
        await msg.stream_token(token)

    await msg.send()
    cl.user_session.set("prompt_history", prompt + msg.content)


@cl.on_message
async def chat(message: cl.Message):
    await call_claude(message.content)
