---
title: 'Langchain Plotly Example'
tags: ['langchain', 'plotly']
---

# Langchain Plotly Example

In this example, a langchain agent is used to parse a CSV file and generate plotly graphs through Chainlit. This is educational and doesn't perform well.

You might want to play with the function call prompt stored in the `description` field of `PlotlyPythonAstREPLTool` to get better results.
The `PlotlyPythonAstREPLTool` class in `PlotlyTool.py` is a specialized tool that allows users to run Python code in a REPL-like environment to create and display Plotly charts. It sanitizes the input code, executes it, and then converts the output to a Plotly chart JSON, which can be sent to the user session for display.

## Setup

For this example, you need to use python 3.9+.

1. Install the requirements:

```bash
pip install chainlit plotly langchain langchain_experimental openai pandas tabulate
```

2. Run the example:

```bash
chainlit run app.py
```

### How It Works

- `app.py` sets up the Chainlit application, defines the `start` and `main` functions for handling the chat start event and incoming messages, respectively.
- The `start` function initializes the langchain agent with the CSV data and the `PlotlyPythonAstREPLTool`.
- The `main` function processes incoming messages, runs the agent to generate responses, and sends Plotly charts to the user if available.

### Function Definitions

- `plotly_chart_creator`: A simple function that creates a Plotly line chart from a CSV dataset and sends it to the user session.
- `start`: An asynchronous function that runs at the start of the chat to set up the langchain agent with the CSV data and tools.
- `main`: The main asynchronous function that handles incoming messages and sends responses or Plotly charts to the user.