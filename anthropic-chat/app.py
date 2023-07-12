
import os
import anthropic
import json
import ast
import chainlit as cl

c = anthropic.Client(os.environ["ANTHROPIC_API_KEY"])


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "prompt_history", "",
    )
    await cl.Avatar(name="Anthropic", 
                    url="https://pbs.twimg.com/profile_images/1398287823229251584/FVs58Hks_400x400.jpg").send()


@cl.on_message
async def chat(message: str):
    prompt_history = cl.user_session.get("prompt_history")

    prompt = f"{prompt_history}{anthropic.HUMAN_PROMPT}{message}{anthropic.AI_PROMPT}"

    ui_msg = cl.Message(
        author="Anthropic",
        content="",
        prompt=prompt
    )

    response = await c.acompletion_stream(
        prompt=prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT],
        max_tokens_to_sample=1000,
        model="claude-2.0", # claude-instant-1.1
        stream=True,
    )

    async for data in response:
        token = data['completion']
        await ui_msg.stream_token(token, is_sequence=True)

    await ui_msg.send()

    prompt_history = prompt + token
    cl.user_session.set("prompt_history", prompt_history)
