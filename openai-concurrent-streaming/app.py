import os
import chainlit as cl
import asyncio

from openai import AsyncClient

openai_client = AsyncClient(api_key=os.environ.get("OPENAI_API_KEY"))


model_name = "gpt-3.5-turbo"
settings = {
    "temperature": 0.3,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": "Characters from the silicon valley tv show are acting. Gilfoyle (sarcastic) wants to push to production. Dinesh (scared) wants to write more tests. Richard asks the question.",
            }
        ],
    )
    await cl.Avatar(
        name="Gilfoyle",
        url="https://static.wikia.nocookie.net/silicon-valley/images/2/20/Bertram_Gilfoyle.jpg",
    ).send()
    await cl.Avatar(
        name="Dinesh",
        url="https://static.wikia.nocookie.net/silicon-valley/images/e/e3/Dinesh_Chugtai.jpg",
    ).send()


async def answer_as(name):
    message_history = cl.user_session.get("message_history")
    msg = cl.Message(author=name, content="")

    stream = await openai_client.chat.completions.create(
        model=model_name,
        messages=message_history + [{"role": "user", "content": f"speak as {name}"}],
        stream=True,
        **settings,
    )
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    # Need to add the information that it was the author who answered but OpenAI only allows assistant.
    # simplified for the purpose of the demo.
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.send()


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    await asyncio.gather(answer_as("Gilfoyle"), answer_as("Dinesh"))
