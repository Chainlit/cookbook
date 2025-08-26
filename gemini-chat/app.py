import os
import chainlit as cl
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Please set it in a .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Welcome to Gemini Flash 2.0 with Chainlit! Ask me anything.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handles user messages and sends responses from Gemini Flash 2.0."""
    try:
        response = await model.generate_content_async(message.content)
        await cl.Message(
            content=response.text,
            author="Gemini Flash 2.0",
        ).send()
    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()


@cl.on_stop
async def on_stop():
    print("User stopped the response.")

@cl.on_chat_end
async def on_chat_end():
    print("Chat ended.")

if __name__ == "__main__":
    cl.run()
