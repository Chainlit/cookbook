---
title: 'OpenInterpreter x Chainlit'
tags: ['openinterpreter', 'chainlit']
---

# Welcome to OpenInterpreter x Chainlit! 🚀🤖

**OpenInterpreter**: https://github.com/KillianLucas/open-interpreter/

**Chainlit**: https://github.com/chainlit/chainlit

Open Interpreter lets LLMs run code (Python, Javascript, Shell, and more) locally. You can chat with Open Interpreter through a ChatGPT-like interface in your terminal by running $ interpreter after installing.


This Chainlit cookbook example allows you to do just that from a web app, with additional UI features such as file uploads, downloads, Images and other UI Elements.

This is an example combining both to provide a code interpreter-like app.

## High-Level Description

The integration allows users to:
1. Select an LLM of their choice.
2. Optionally upload files to be used by the LLM.
3. Interact with the LLM through a chat interface, sending and receiving messages that can include code execution requests.

## Quickstart

To get started with this integration, follow these steps:

1. **Install OpenInterpreter**: Follow the installation instructions on the [OpenInterpreter GitHub page](https://github.com/KillianLucas/open-interpreter/).

2. **Install Chainlit**: Chainlit can be installed via pip:
```shell
pip install chainlit
```

3. **Set Up Environment Variables**: Ensure that your OpenAI API key is set as an environment variable:
```shell
export OPENAI_API_KEY='your_api_key_here'
```

4. **Run the Application**: Navigate to the directory containing the `app.py` file and run:
```shell
chainlit run app.py
```

5. **Interact with the Web App**: Open your web browser to the address provided by Chainlit (usually `http://localhost:8501`) and start interacting with the application.

## Code Definitions

- `CustomStdout`: A class that overrides the standard output to redirect print statements to the Chainlit UI.
- `CustomStdin`: A class that overrides the standard input to receive input from the Chainlit UI.
- `@cl.on_chat_start`: A decorator that initializes the custom standard input/output classes and sets up the chat settings.
- `@cl.on_settings_update`: A decorator that updates the selected LLM model based on user input.
- `@cl.on_message`: A decorator that handles incoming messages, processes file uploads, and interacts with the OpenInterpreter.

[Demo](openinterpreter/openinterpreter-chainlit.mp4)

---

Enjoy the power of LLMs in your browser with OpenInterpreter x Chainlit!