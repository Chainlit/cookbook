import os
from typing import Any

import chainlit as cl


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # TODO: Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == (os.getenv("DEFAULT_USERNAME", "admin"), os.getenv("DEFAULT_USER_PASSWORD")):
        return cl.User(
            identifier=os.getenv("DEFAULT_USERNAME"),
            metadata={"role": "admin",
                      "provider": "credentials"}
        )
    else:
        return None


@cl.set_chat_profiles
async def load_chat_profiles():
    return [
        cl.ChatProfile(
            name="ChatGPT",
            markdown_description="ChatGPT by OpenAI",
            icon="https://github.com/ndamulelonemakh/remote-assets/blob/7ed514dbd99ab86536daf3942127822bd979936c/images/openai-logomark.png?raw=true",
        ),
        cl.ChatProfile(
            name="Claude",
            markdown_description="Claude by Anthropic",
            icon="https://www.anthropic.com/images/icons/apple-touch-icon.png",
        ),
        cl.ChatProfile(
            name="Gemini",
            markdown_description="Germini Pro by Google and DeepMind",
            icon="https://github.com/ndamulelonemakh/remote-assets/blob/main/images/Google-Bard-Logo-758x473.jpg?raw=true",
        )
    ]


@cl.on_settings_update
async def setup_agent(settings: dict[str, Any]):
    cl.logger.debug(f"user settings updated: {settings}")
    existing_settings: dict = cl.user_session.get("chat_settings", {})
    existing_settings.update(settings)
    if "max_tokens" in existing_settings:
        existing_settings["max_tokens"] = int(existing_settings["max_tokens"])
    if "max_tokens_to_sample" in existing_settings:
        existing_settings["max_tokens_to_sample"] = int(existing_settings["max_tokens_to_sample"])
    cl.user_session.set("chat_settings", existing_settings)


@cl.on_chat_start
async def start_chat():
    active_chat_profile = cl.user_session.get("chat_profile")
    if active_chat_profile == "ChatGPT":
        from src.providers.chatgpt import AVATAR, chat_settings, call_chatgpt, user_setttings

        cl.user_session.set("prompt_history", [])
        cl.user_session.set("call_llm", call_chatgpt)
        cl.user_session.set("chat_settings", chat_settings)
        s = cl.ChatSettings(user_setttings)
        await s.send()

        await AVATAR.send()

    elif active_chat_profile == "Claude":
        from src.providers.claude import AVATAR, chat_settings, call_claude, user_setttings

        cl.user_session.set("prompt_history", "")
        cl.user_session.set("call_llm", call_claude)
        cl.user_session.set("chat_settings", chat_settings)
        s = cl.ChatSettings(user_setttings)
        await s.send()

        await AVATAR.send()
    elif active_chat_profile == "Gemini":
        from src.providers.gemini import AVATAR, chat_settings, call_gemini, user_setttings
        cl.user_session.set("prompt_history", [])
        cl.user_session.set("call_llm", call_gemini)
        cl.user_session.set("chat_settings", chat_settings)
        s = cl.ChatSettings(user_setttings)
        await s.send()

        await AVATAR.send()
    else:
        await cl.ErrorMessage(f"Unsupported profile: {active_chat_profile}").send()
        return

    await cl.Message(f"Welcome back, ##TODO-USERNAME. {active_chat_profile} is ready to fulfill your requests!").send()


@cl.on_message
async def chat(message: cl.Message):
    chat_callback = cl.user_session.get("call_llm")
    chat_settings = cl.user_session.get("chat_settings")
    await chat_callback(message.content, chat_settings)
