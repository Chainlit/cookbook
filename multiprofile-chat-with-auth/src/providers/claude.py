import os

from typing import Any

import anthropic
import chainlit as cl
from chainlit.playground.providers import Anthropic
from chainlit.input_widget import Select, Slider

anthropic_client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
AVATAR = cl.Avatar(
        name="Claude",
        url="https://www.anthropic.com/images/icons/apple-touch-icon.png",
)
chat_settings = settings = {
        "stop_sequences": [anthropic.HUMAN_PROMPT],
        "max_tokens_to_sample": 1000,
        "model": "claude-2.0",
}
user_setttings = [
    Select(
        id="model",
        label="Model",
        # https://docs.anthropic.com/claude/docs/models-overview#claude-3-a-new-generation-of-ai
        values=["claude-2.1", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        initial_index=0,
    ),
    Slider(
                id="temperature",
                label="Temperature",
                initial=0.2,
                min=0,
                max=1,
                step=0.1,
            ),
    Slider(
                id="max_tokens_to_sample",
                label="Maxiumum Completions Tokens",
                initial=1000,
                min=100,
                max=32000,
                step=10,
                description="The maximum allowable tokens in the response",
    ),
    
]


@cl.step(name="Claude", 
         type="llm", 
         root=True)
async def call_claude(query: str, settings: dict[str, Any] = None):
    prompt_history = cl.user_session.get("prompt_history")
    prompt = f"{prompt_history}{anthropic.HUMAN_PROMPT}{query}{anthropic.AI_PROMPT}"

    settings = settings or chat_settings
    if "max_tokens_to_sample" in settings:
        settings["max_tokens_to_sample"] = int(settings["max_tokens_to_sample"])
    stream = await anthropic_client.completions.create(
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
