---
title: 'AutoGen with Chainlit'
tags: ['autogen', 'chainlit']
---

# AutoGen with Chainlit

This repository demonstrates the integration of [AutoGen](https://microsoft.github.io/autogen/) with Chainlit to create an interactive chat application that can execute code and perform tasks such as plotting a chart of stock price changes and saving it to disk.

![AutoGen with Chainlit Example](https://github.com/Chainlit/cookbook/assets/494686/c5d608bd-7480-42cc-b21f-74989d52fd8c)

## Quickstart

Follow these steps to get started with AutoGen and Chainlit:

### Setup

1. (Optional) Create and activate a Python virtual environment:
    
```shell
python3 -m venv venv
source venv/bin/activate
```
2. Install the required dependencies:
        
```shell 
pip install chainlit pyautogen
```

3. Copy the `.env.sample` file to a new `.env` file and replace the `api_key` value with your own OpenAI API key.
4. Run the Chainlit app:

- You can modify the initial AutoGen prompt in the `app.py` file to change the task.

### Notes

- Do not run with `chainlit run app.py -w` as it may cause unexpected behavior.
- You can monkey-patch methods of the `Agent` class if needed, instead of creating a subclass.

## Code Overview

The `app.py` file contains the main logic for the Chainlit chat application. It defines custom `Agent` classes that handle sending messages and processing user input.

- `ChainlitAssistantAgent`: A subclass of `AssistantAgent` that sends messages to other agents.
- `ChainlitUserProxyAgent`: A subclass of `UserProxyAgent` that handles user input and can send messages to other agents.

The `async_app.py` file is a placeholder for future asynchronous support, pending the resolution of an issue in the AutoGen library.

To change the task, modify the `TASK` variable in `app.py` with the desired prompt.

## Running the Application

To start the application, use the following command: 
    
```shell
chainlit run app.py
```

This will initiate a chat session where the user can interact with the assistant agent to perform tasks such as generating a plot for NVDA stock price change YTD.

For more detailed information on the functions and classes used, refer to the source code in the `app.py` and `async_app.py` files.