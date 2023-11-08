import os

from openai import AsyncOpenAI
import asyncio

from dotenv import load_dotenv

load_dotenv()


api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)


async def create():
    assistant = await client.beta.assistants.create(
        name="Math Tutor",
        instructions="You are a personal math tutor. Write and run code to answer math questions.",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
    )
    print(assistant)
    # SAVE IT IN .env


asyncio.run(create())
