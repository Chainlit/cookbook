---
title: 'Agent Prompt Playground'
tags: ['prompt-playground', 'chainlit']
---

# Agent Prompt Playground

The Agent Prompt Playground is an interactive environment within the ChainLit framework that enables developers to experiment with and refine their language model prompts. This tool facilitates the visualization, iteration, and versioning of prompts, which is crucial for improving the development and debugging workflows.

## Key Features

- **Interactive Prompt Testing:** Test and modify prompts in real-time to see how the language model responds.
- **Version Control:** Keep track of changes to prompts over time, allowing for easy reversion and understanding of prompt evolution.
- **Visualization:** Gain insights into how prompts are processed and how responses are generated.

## Quickstart

To get started with the Agent Prompt Playground, follow these steps:

1. **Set up your environment:**
Ensure you have Python installed and the necessary packages by running:
```shell
pip install chainlit langchain
```

2. **Configure the LLM Provider:**
In `app.py`, set up the language model you want to use by configuring the `HuggingFaceHub` with the appropriate model and API token.

3. **Initialize the Playground:**
Use the provided `on_chat_start` and `on_message` functions to initialize the playground and handle incoming messages.

4. **Run the Application:**
Execute `chainlit run app.py` to start the Agent Prompt Playground. Interact with the language model and refine your prompts as needed.

## Code Definitions

- `HuggingFaceHub`: A class that interfaces with the HuggingFace Model Hub, allowing you to use models hosted there.
- `ChatPromptTemplate`: A template for constructing chat prompts that can be sent to the language model.
- `StrOutputParser`: A parser that converts the language model's output into a string.
- `Runnable`: An abstraction that represents a sequence of operations that can be executed.
- `RunnableConfig`: Configuration for the `Runnable`, including callback handlers.

More info and a video here: https://docs.chainlit.io/concepts/prompt-playground/overview
