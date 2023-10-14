# Agent Prompt Playground
The Prompt Playground is a unique feature that allows developers to visualize, iterate, and version prompts, thereby enhancing the development/debugging process.

More info and a video here: https://docs.chainlit.io/concepts/prompt-playground/overview

## Custom Provider Example

This repository serves as an example of how to build a custom provider for Chainlit. In particular, it demonstrates how to leverage all the Langchain LLMs that use `model_kwargs`.

### Files

#### `custom_provider.py`

This file contains the implementation of the `LangChainModelKwargsGenericProvider` class, which is a custom provider for Chainlit. It extends the `BaseProvider` class and provides methods for converting prompt messages, formatting messages, and creating completions. It also includes an example of how to filter and update the `model_kwargs` based on the prompt settings.

#### `app.py`

This file demonstrates how to use the custom provider in a Chainlit application. It imports the `LangChainModelKwargsGenericProvider` class from `custom_provider.py` and instantiates an LLM using the `HuggingFaceHub` class. It then adds the custom provider to the Chainlit configuration and sets up a prompt template and an LLM chain for processing messages.

### Usage

To use this custom provider example, follow these steps:

1. Import the `LangChainModelKwargsGenericProvider` class from `custom_provider.py` into your application.
2. Instantiate an LLM using the desired LLM class (e.g., `HuggingFaceHub`) and set the `model_kwargs` as needed.
3. Add the custom provider to the Chainlit configuration using the `add_llm_provider` function, passing in the `LangChainModelKwargsGenericProvider` instance.
4. Set up a prompt template and an LLM chain for processing messages, as shown in `app.py`.
5. Run your Chainlit application and interact with the LLM using the provided prompt template.

### Conclusion

Building a custom provider for Chainlit allows you to extend its functionality and leverage the power of Langchain LLMs that use `model_kwargs`. This example repository provides a starting point for creating your own custom providers and integrating them into your Chainlit applications.

Title : Agent Playground Langchain Model Kwargs
Tags : [playground, langchain]