import os
import time
from openai import AsyncOpenAI

import chainlit as cl

client = AsyncOpenAI(
    api_key=os.getenv("DEEP_SEEK_API_KEY"),
    base_url="https://api.deepseek.com"
    )

@cl.on_message
async def on_message(msg: cl.Message):
    start = time.time()
    stream = await client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are an helpful assistant"},
            *cl.chat_context.to_openai()
        ],
        stream=True
    )

    # Flag to track if we've exited the thinking step
    thinking_completed = False
    
    # Streaming the thinking
    async with cl.Step(name="Thinking") as thinking_step:
        async for chunk in stream:
            delta = chunk.choices[0].delta
            reasoning_content = getattr(delta, "reasoning_content", None)
            if reasoning_content is not None and not thinking_completed:
                await thinking_step.stream_token(reasoning_content)
            elif not thinking_completed:
                # Exit the thinking step
                thought_for = round(time.time() - start)
                thinking_step.name = f"Thought for {thought_for}s"
                await thinking_step.update()
                thinking_completed = True
                break
    
    
    final_answer = cl.Message(content="")

    # Streaming the final answer
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            await final_answer.stream_token(delta.content)
            
    await final_answer.send()