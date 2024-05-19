import os
import chainlit as cl
import asyncio

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def create_assistant():
    assistant = await client.beta.assistants.create(
        name="General Assistant",
        instructions="You are an AI assistant. Please help the user with their queries.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",
    )
    return assistant


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    assistant = loop.run_until_complete(create_assistant())
    print(f"Assistant created with ID: {assistant.id}")

