import os
import anthropic
import chainlit as cl
from chainlit.playground.providers import Anthropic

c = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "prompt_history",
        "",
    )
    await cl.Avatar(
        name="Claude",
        url="https://www.anthropic.com/images/icons/apple-touch-icon.png",
    ).send()


@cl.step(name="Claude", type="llm", root=True)
async def call_claude(query: str):
    prompt_history = cl.user_session.get("prompt_history")

    prompt = f"{prompt_history}{anthropic.HUMAN_PROMPT}{query}{anthropic.AI_PROMPT}"

    settings = {
        "stop_sequences": [anthropic.HUMAN_PROMPT],
        "max_tokens_to_sample": 1000,
        "model": "claude-2.0",
    }

    stream = await c.completions.create(
        prompt=prompt,
        stream=True,
        **settings,
    )

    async for data in stream:
        token = data.completion
        await cl.context.current_step.stream_token(token)

    cl.context.current_step.generation = cl.CompletionGeneration(
        formatted=prompt,
        completion=cl.context.current_step.output,
        settings=settings,
        provider=Anthropic.id,
    )

    cl.user_session.set("prompt_history", prompt + cl.context.current_step.output)


@cl.on_message
async def chat(message: cl.Message):
    await call_claude(message.content)
