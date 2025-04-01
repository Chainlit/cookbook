# AI Web search with Linkup

This project demonstrates how to create a chatbot using [Chainlit](https://docs.chainlit.io/get-started/overview) and [Linkup](https://linkup.so/), enabling powerful web search capabilities and enhancing answers.

## Overview

- Seamlessly integrates Chainlit's chat interface with Linkup's search capabilities
- Leverages function calling to provide dynamic search functionality
- Demonstrates a production-ready pattern for building AI assistants with web search
- Supports easy customization and extension with additional tools

## Features

- Real-time web search: Retrieve up-to-date information from the internet
- Function calling integration: Structured approach to tool integration
- Model flexibility: Easy to switch between different LLMs

## Quick Start

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set your Anthropic and Linkup API keys in a .env file similar to .env.example:

   ```
   ANTHROPIC_API_KEY=your_api_key_here
   LINKUP_API_KEY=your_api_key_here
   ```

You can get your Linkup API key [here](https://app.linkup.so/api-keys)

3. Run the app:

   ```
   chainlit run app.py
   ```

4. Open your browser and navigate to http://localhost:8000

## Key Components

1. **Tools**:

   - `search_web`: Performs a web search using Linkup SDK
   - Easily extensible with additional tool functions

2. **Chainlit Setup**:

   - `@cl.on_chat_start`: Initializes chat session with a search [command](https://docs.chainlit.io/concepts/command) available
   - `@cl.on_message`: Handles user messages and processes responses

3. **LLM Integration**:

   - `run_with_tools`: Manages communication with the selected LLM.
   - Uses `litellm` to support multiple model providers without code changes
   - Handles streaming responses for real-time feedback

4. **Function Calling**:
   - `process_tool_calls`: Executes the appropriate tools based on LLM decisions
   - Supports structured interaction between the LLM and external tools

## How It Works

- User sends a message or triggers the search command
- The message is processed and sent to the LLM
- If the LLM determines web search is needed, it calls the search function
- Linkup API performs the search and returns relevant results
- The LLM formulates a response using the search results
- The response is displayed to the user with sources when available

## Customization

- Add new tools to the `tools` list to extend functionality
- Modify the `truncate_messages` function to adjust context window usage
- Modify `DEFAULT_MODEL` to use different LLMs (Claude, GPT, etc.)
- Customize the chat interface using Chainlit's configuration options

## Troubleshooting

- Ensure API keys are correctly set in the .env file
- Check that all dependencies are installed
- Verify network connectivity for API calls
- Consult the [Linkup](https://docs.linkup.so/) and [Chainlit](https://docs.chainlit.io/get-started/overview) documentation for specific issues

## Note

This is a demonstration project. While the implementation is straightforward, in a production environment, you should:

- Add proper error handling and implement retry mechanisms
- Use a more robust architecture
- Ensure that the message history strictly follows your LLM provider's requirements for message ordering (e.g., messages must alternate between user and assistant roles, and always start with a user message)
