# Chainlit Anthropic Example with Function Calling

This project demonstrates how to create a chatbot using Chainlit and Anthropic's Claude AI model, showcasing function calling capabilities with example tools.

## Overview

- Integrates Chainlit with Claude 3 Sonnet model
- Demonstrates function calling with two example tools:
  - Mock weather lookup
  - Simple calculator

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key in a .env file similar to .env.example:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. Run the app:
   ```
   chainlit run app.py
   ```

## Key Components

1. **Example Tools**:
   - `get_current_weather`: Returns mock weather data
   - `calculator`: Performs basic arithmetic

2. **Chainlit Setup**:
   - `@cl.on_chat_start`: Initializes chat session
   - `@cl.on_message`: Handles user messages

3. **Claude Integration**:
   - `call_claude`: Manages communication with Claude

4. **Function Calling**:
   - `@cl.step(type="tool")`: Handles tool execution
   - `call_tool`: Routes to appropriate tool function

## Customization

- Add new tools to the `tools` list
- Implement corresponding functions in `TOOL_FUNCTIONS`
- Modify `SYSTEM` prompt or `MODEL_NAME` as needed

## Note

This is a demonstration project. The weather tool uses mock data, and the calculator is basic. In a production environment, replace these with real APIs and more robust implementations.