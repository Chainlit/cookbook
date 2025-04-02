# MCP OpenAI-Gemini Cookbook

This cookbook demonstrates how to create a Chainlit MCP application that works seamlessly with both Google Gemini and OpenAI models using a single codebase. The application leverages the OpenAI SDK's compatibility with Google AI Studio models.

## Overview

This application:
- Uses Chainlit for the chat interface
- Supports OpenAI models (GPT-4, etc.)
- Supports Google Gemini models
- Integrates with Model Control Protocol (MCP) for tool/function calling
- Handles tool execution with proper error management

## Setup

### Prerequisites
- Python 3.9+
- An API key from either OpenAI or Google AI Studio

### Environment Variables

Create a `.env` file with the following:

```
# For Google Gemini
API_KEY=your_google_ai_studio_key
MODEL_NAME=gemini-2.0-flash

# For OpenAI (uncomment these when using OpenAI)
# API_KEY=your_openai_key
# MODEL_NAME=gpt-4-turbo
```

## Configuration

### Using Google Gemini Models

The default configuration in this cookbook is set up for Google Gemini. When using Gemini models:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta"
)
```

Make sure your `MODEL_NAME` is set to a valid Gemini model like `gemini-2.0-flash`.

### Using OpenAI Models

To use OpenAI models instead, modify the client initialization.

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=API_KEY
    base_url="https://api.openai.com/v1"
)
```

And set your `MODEL_NAME` to a valid OpenAI model like `gpt-4o`.

## Running the Application

Start the application with:

```bash
chainlit run app.py
```

## How It Works

This cookbook leverages the fact that Google AI Studio models can be accessed through the OpenAI SDK, making it possible to switch between providers with minimal code changes. The application:

1. Initializes client based on your configuration
2. Sets up MCP tools and connections
3. Processes user messages using the selected LLM
4. Handles tool/function calls seamlessly
5. Manages chat history and UI updates

## Resources

- [Google AI Gemini API OpenAI SDK Compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Google AI Studio](https://aistudio.google.com/)
- [Chainlit Documentation](https://docs.chainlit.io)

## Notes

- Function/tool calling capabilities may vary between OpenAI and Gemini models
- API responses might have slight differences in structure between providers
- Always check the latest compatibility documentation as both APIs evolve
