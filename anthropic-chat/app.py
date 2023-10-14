import os
import anthropic
import chainlit as cl
from chainlit.prompt import Prompt
from chainlit.playground.providers import Anthropic

c = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "prompt_history",
        "",
    )
    await cl.Avatar(
        name="Anthropic",
        url="https://pbs.twimg.com/profile_images/1398287823229251584/FVs58Hks_400x400.jpg",
    ).send()


@cl.on_message
async def chat(message: cl.Message):
    prompt_history = cl.user_session.get("prompt_history")

    prompt = f"{prompt_history}{anthropic.HUMAN_PROMPT}{message.content}{anthropic.AI_PROMPT}"

    settings = {
        "stop_sequences": [anthropic.HUMAN_PROMPT],
        "max_tokens_to_sample": 1000,
        "model": "claude-2.0",
    }

    ui_msg = cl.Message(
        author="Anthropic",
        content="",
    )

    stream = await c.completions.create(
        prompt=prompt,
        stream=True,
        **settings,
    )

    async for data in stream:
        token = data.completion
        await ui_msg.stream_token(token)

    ui_msg.prompt = Prompt(
        formatted=prompt,
        completion=ui_msg.content,
        settings=settings,
        provider=Anthropic.id,
    )

    await ui_msg.send()

    prompt_history = prompt + token
    cl.user_session.set("prompt_history", prompt_history)
