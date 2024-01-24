---
title: 'Llama Index Google Docs QA'
tags: ['llama', 'index', 'google', 'docs', 'qa']
---

# Llama Index Google Docs QA

This Python application integrates a question-answering system using the Llama Index with Google Docs as the data source. It leverages OpenAI's GPT models for generating responses and ChainLit for creating interactive chat applications.

## Description

The application defines a function `load_context()` that either loads a pre-existing index from storage or creates a new one by reading documents from Google Docs. It uses the `LLMPredictor` with the `ChatOpenAI` model for predictions and a `PromptHelper` for managing the context of the interactions.

Upon starting a chat session, the application initializes the query engine and sets it in the user session. When a user sends a message, the application uses the query engine to generate a response based on the content of the Google Docs and streams the response back to the user.

## Quickstart

1. Set your OpenAI API key in your environment variables.
2. Define the Google Docs IDs you want to index in the `load_context()` function.
3. Run the application to start interacting with the chatbot.

### Function Definitions

- `load_context()`: Loads the index from storage or creates a new one if storage is not found. It initializes necessary components like `LLMPredictor`, `PromptHelper`, and `ServiceContext`.
- `start()`: An asynchronous function that is triggered when a chat starts. It loads the context and sets up the query engine.
- `main(message: cl.Message)`: The main asynchronous function that handles incoming messages and uses the query engine to generate and send responses.