import openai
import os
import chainlit as cl
import asyncio

openai.api_key = os.environ.get("OPENAI_API_KEY")

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

    async for stream_resp in await openai.ChatCompletion.acreate(
        model=model_name,
        messages=message_history + [{"role": "user", "content": f"speak as {name}"}],
        stream=True,
        **settings,
    ):
        token = stream_resp.choices[0]["delta"].get("content", "")
        await msg.stream_token(token)

    # Need to add the information that it was the author who answered but OpenAI only allows assistant.
    # simplified for the purpose of the demo.
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.send()


@cl.on_message
async def main(message: str):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message})

    await asyncio.gather(answer_as("Gilfoyle"), answer_as("Dinesh"))

def modify_message_history(message_history):
  """Modifies the message history in some way.

  Args:
    message_history: A list of dictionaries, where each dictionary represents a
      message.

  Returns:
    A modified list of dictionaries, where each dictionary represents a message.
  """

  # Add a new message to the message history.
  message_history.append({"role": "system", "content": "This is a new message."})

  # Remove the oldest message from the message history.
  message_history.pop(0)

  return message_history
