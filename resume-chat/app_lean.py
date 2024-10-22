from operator import itemgetter
import os
from mistralai import Mistral
from dotenv import load_dotenv

from chainlit.types import ThreadDict
import chainlit as cl

load_dotenv()

@cl.password_auth_callback
def auth():
    return cl.User(identifier="test")


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    cl.user_session.set("chat_history", [])

    # user_session = thread["metadata"]
    
    for message in thread["steps"]:
        if message["type"] == "user_message":
            cl.user_session.get("chat_history").append({"role": "user", "content": message["output"]})
        elif message["type"] == "assistant_message":
            cl.user_session.get("chat_history").append({"role": "assistant", "content": message["output"]})


@cl.on_message
async def on_message(message: cl.Message):
    # Note: by default, the list of messages is saved and the entire user session is saved in the thread metadata
    chat_history = cl.user_session.get("chat_history")

    api_key = os.environ["MISTRAL_API_KEY"]
    model = "ministral-8b-latest"

    client = Mistral(api_key=api_key)

    chat_history.append({"role": "user", "content": message.content})

    chat_response = client.chat.complete(
        model=model,
        messages=chat_history
    )
    
    response_content = chat_response.choices[0].message.content

    chat_history.append({"role": "assistant", "content": response_content})

    await cl.Message(content=response_content).send()
