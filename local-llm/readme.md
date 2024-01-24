---
title: 'ChainLit Local LLM Integration'
tags: ['chainlit', 'local', 'llm']
---

# ChainLit Local LLM Integration

This repository contains examples of integrating various local Large Language Models (LLMs) with ChainLit, a framework for building interactive applications with LLMs. Each example demonstrates how to set up a different LLM for use within the ChainLit environment.

## Description

The examples provided showcase how to integrate different LLMs, such as `Ollama`, `LlamaCpp`, and `HuggingFacePipeline`, into the ChainLit framework. These integrations allow users to interact with the models through a chat interface, where the models can provide responses based on their specialized capabilities, such as generating source code or providing historical information.

## Quickstart

To get started with these examples, follow the steps below:

1. Clone the repository to your local machine.
2. Install the required dependencies for ChainLit and the respective LLMs.
3. Choose the LLM you want to work with and navigate to its corresponding Python file.
4. Update any necessary paths or configurations, such as the `MODEL_PATH` for `LlamaCpp`.
5. Run the ChainLit application to start interacting with the LLM through the chat interface.

### Function Definitions

#### Ollama Integration (`ollama.py`)

- `on_chat_start`: Initializes the chat session with a historical context prompt.
- `on_message`: Streams the user's message to the model and sends back the model's response.

#### LlamaCpp Integration (`llama-cpp.py`)

- `instantiate_llm`: Loads the LlamaCpp model with the specified configuration.
- `main` (decorated with `@cl.on_chat_start`): Sets up the conversation chain with a system prompt for code generation.
- `main` (decorated with `@cl.on_message`): Handles incoming messages and generates responses using the conversation chain.

#### Llama2 Chat Integration (`llama2-chat.py`)

- `load_llama`: Loads the Llama2 model from HuggingFace with the specified tokenizer and streamer.
- `main` (decorated with `@cl.on_chat_start`): Initializes the LLM chain with a prompt for answering questions.
- `run`: Processes incoming messages and provides responses using the LLM chain.


