---
title: 'OpenAI Parallel Function Calling'
tags: ['openai', 'tools']
---

# Chainlit Cookbook: OpenAI Concurrent Functions

This is a guide to the code example provided in the `chainlit-cookbook/openai-concurrent-functions` directory. The code demonstrates how to use Chainlit, a powerful tool for prototyping, debugging, and sharing applications built on top of Language Learning Models (LLMs), in conjunction with OpenAI's GPT-4 model.

## Overview

The code example is a simple chatbot that uses the GPT-4 model to generate responses. It also includes a dummy function `get_current_weather` that returns a hardcoded weather report. This function is used to demonstrate how to call a function from within the chatbot.

## Key Components

- `get_current_weather`: This function takes a location and a unit (either "celsius" or "fahrenheit") as input and returns a hardcoded weather report in the form of a JSON string.

- `run_conversation`: This function is the main loop of the chatbot. It takes a message as input, appends it to the message history, and then alternates between calling the `call_gpt4` function and processing its responses until a maximum number of iterations is reached.

## Usage

To use this code, you need to have an OpenAI API key, which you can obtain from the OpenAI website. You also need to have the Chainlit library installed. You can then run the code using a Python interpreter.

Please note that this is a simplified example and is not intended for production use. In a real-world application, you would likely replace the `get_current_weather` function with a call to a real weather API, and you would add error handling code to deal with potential issues such as API rate limits or network errors.
