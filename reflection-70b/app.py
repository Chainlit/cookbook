import requests
import os
import chainlit as cl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def call_model(messages):
    # Model ID for production deployment
    model_id = os.getenv("MODEL_ID")
    # Read secrets from environment variables
    baseten_api_key = os.getenv("BASETEN_API_KEY")
    # Call model endpoint
    resp = requests.post(
        f"https://model-{model_id}.api.baseten.co/production/predict",
        headers={"Authorization": f"Api-Key {baseten_api_key}"},
        json={
            "messages": messages,
            "max_tokens": 1024
        },
        stream=True
    )

    # Stream the generated tokens
    for content in resp.iter_content():
        yield content.decode("utf-8")


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Reflection-70B",
            message="how many R's are there in Strawberry?"
        )
    ]


@cl.on_chat_start
def init_history():
    system_prompt = "You are a world-class AI system, capable of complex reasoning and reflection. Reason through the query inside <thinking> tags, and then provide your final response inside <output> tags. If you detect that you made a mistake in your reasoning at any point, correct yourself inside <reflection> tags."

    message_history = [
        {"role": "system", "content": system_prompt}]
    cl.user_session.set("history", message_history)


@cl.on_message
async def main(message: cl.Message):
    # Get the current message history
    message_history = cl.user_session.get("history")

    # Add the user's message to the history
    message_history.append({"role": "user", "content": message.content})

    # RAW
    # msg = cl.Message(content="")
    # # option 1
    # for chunk in call_model(message_history):
    #     if chunk:
    #         await msg.stream_token(chunk)
    # msg.send()
    # # Add the assistant's response to the history
    # message_history.append({"role": "assistant", "content": msg.content})

    raw_answer = ""
    is_thinking = False
    is_answering = False

    for chunk in call_model(message_history):
        raw_answer += chunk
        if raw_answer.endswith("<thinking>"):
            is_thinking = True
            msg = cl.Message(author="Thinking", content="<thinking>")
            await msg.send()
        elif raw_answer.endswith("</thinking>"):
            await msg.stream_token(chunk)
            is_thinking = False
            await msg.update()
        elif raw_answer.endswith("<output>"):
            is_answering = True
            msg = cl.Message(author="Answer", content="<output>")
            await msg.send()
        elif raw_answer.endswith("</output>"):
            await msg.stream_token(chunk)
            is_answering = False
            await msg.update()
        elif chunk and (is_thinking or is_answering):
            await msg.stream_token(chunk)

    message_history.append({"role": "assistant", "content": raw_answer})
    # Update the session history
    cl.user_session.set("history", message_history)
