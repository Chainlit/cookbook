---
title: 'LiteLLM Thinking Models Integration'
tags: ['litellm', 'thinking', 'streaming']
---

# LiteLLM Thinking Models Integration

This repository demonstrates how to integrate thinking-enabled LLMs (like Qwen, DeepSeek-R1) with ChainLit using LiteLLM.

## Description

The integration showcases how to connect to any thinking-capable model through LiteLLM's unified API. The application captures and streams the model's internal reasoning process in real-time, allowing users to observe how the model thinks through problems step-by-step before providing final answers.

### Function Definitions

#### Thinking LLM Integration (`thinking_llm.py`)

- `start_chat`: Initializes chat session with system prompt and message history
- `reasoning_step`: ChainLit step that captures and streams reasoning content
- `on_message`: Handles user messages, coordinates thinking display and final response streaming
- `client`: Configured LiteLLM client with partial application for consistent model parameters

### Configuration
[!IMPORTANT]
Replace `.chainlit/config.toml` to `config.toml` to apply the custom CSS and JS.

```python
# Example using ollama but can adopt to any given litellm 
LLM_MODEL_NAME = "ollama/qwen3:latest"
API_BASE_URL = "http://localhost:11434"  # Provider endpoint
```

The application separates the thinking process into a dedicated ChainLit step, allowing users to see the model's reasoning before the final response.
