---
title: 'Resume-Chat Application'
tags: ['chainlit', 'langchain']
---

# Resume-Chat Application

This application is designed to facilitate a chat session with a bot that can resume conversations. It uses the `chainlit` and `langchain` libraries to manage chat sessions and interactions with an AI model.

## High-Level Description

The application initializes a chatbot using the `ChatOpenAI` model, which is capable of streaming responses. It sets up a conversation memory to remember the chat history and uses a prompt template to structure the interaction with the user. The chatbot is designed to be helpful and maintain the context of the conversation even after interruptions.

## Key Functions

- `setup_runnable()`: Initializes the chatbot with a memory buffer and a prompt template, and sets up the runnable pipeline for processing messages.
- `auth()`: A callback function for password authentication, returning a test user.
- `on_chat_start()`: An asynchronous function that is triggered when a chat starts, setting up the memory and runnable for the session.
- `on_chat_resume(thread: ThreadDict)`: An asynchronous function that resumes a chat from a given thread, repopulating the memory with the conversation history.
- `on_message(message: cl.Message)`: An asynchronous function that handles incoming messages, processes them through the runnable, and sends responses back to the user.

## Quickstart

To start using this application, follow these steps:

1. Ensure you have `chainlit` and `langchain` libraries installed.
2. Place the provided code in a file named `app.py` within the `chainlit-cookbook/resume-chat` directory.
3. Run the application. It will listen for chat start, resume, and message events.
4. Interact with the chatbot through the supported interface, and it will maintain the conversation context across sessions.

## Code Definitions

- `Runnable`: A composable unit of execution in the `langchain` library.
- `ConversationBufferMemory`: A `langchain` class that stores the conversation history.
- `ThreadDict`: A `chainlit` type representing the thread of conversation steps.