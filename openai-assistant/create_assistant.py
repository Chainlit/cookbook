import os

from openai import AsyncOpenAI
import asyncio

from dotenv import load_dotenv

load_dotenv()


api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)


async def create():
    instructions = """You are a personal math tutor. Write and run code to answer math questions.
Reply in markdown, especially for math expressions using the $$ expression.

Example:
Given a formula below $$ s = ut + \frac{1}{2}at^{2} $$ Calculate the value of $s$ when $u = 10\frac{m}{s}$ and $a = 2\frac{m}{s^{2}}$ at $t = 1s$
"""
    assistant = await client.beta.assistants.create(
        name="Math Tutor",
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
    )
    print(assistant)
    # SAVE IT IN .env


asyncio.run(create())
