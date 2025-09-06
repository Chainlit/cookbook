from functools import partial
import chainlit as cl
from litellm import acompletion


LLM_MODEL_NAME: str = "ollama/qwen3:latest"
API_BASE_URL: str = "http://localhost:11434"


client = partial(
    acompletion,
    model=LLM_MODEL_NAME,
    api_base=API_BASE_URL,
    stream=True,
    top_p=0.9,
    temperature=0.2,
    think=True,
)


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {
                "content": "Act like a professional communication strategist",
                "role": "system",
            }
        ],
    )


@cl.step(name="Reasoning", show_input=False)
async def reasoning_step(stream):
    current_step = cl.context.current_step

    async for reason in stream:
        chunk = reason.choices[0].delta
        if not hasattr(chunk, "reasoning_content"):
            break

        else:
            await current_step.stream_token(chunk.reasoning_content)



@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})
    final_message = cl.Message(content="", author="Assistant")

    response = await client(
        messages=message_history, 
    )

    ai_response = ""
    async for chunkie in response:
        chunk = chunkie.choices[0].delta
        has_reasoning = hasattr(chunk, "reasoning_content")

        if has_reasoning:
            await reasoning_step(response)
        else:
            ai_response += chunk.content or ""
            await final_message.update()
        await final_message.stream_token(chunk.content)
        

    if ai_response:
        message_history.append({"role": "assistant", "content": ai_response})
        cl.user_session.set("message_history", message_history)


