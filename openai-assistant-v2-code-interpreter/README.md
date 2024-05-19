---
title: 'Chainlit OpenAI Assistant V2'
tags: ['chainlit', 'openai-assistant']
---

# Chainlit and OpenAI Assistant streaming


The `app.py` file is a crucial component of the OpenAI Assistant V2 code interpreter project. It primarily handles the interaction between the user and the AI assistant through the Chainlit framework. The file includes the setup of the AsyncOpenAI client using an API key, and defines an `EventHandler` class to manage the events triggered during the assistant's operation.

Key functionalities include:
- Initializing and managing messages and tool calls.
- Handling different types of events such as text creation, text updates, and tool call responses.
- Streaming and processing user messages through the assistant in a chat-like interface.

This setup allows the assistant to effectively process and respond to user queries, leveraging the capabilities of OpenAI's models and tools.

## Improvements

- File upload and image capabilities
- More structure with Runs and Steps (https://docs.chainlit.io/api-reference/step-decorator)
- Leverage Literal AI to monitor