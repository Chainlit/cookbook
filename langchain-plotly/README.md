# Langchain Plotly Example

In this example, a langchain agent is used to parse a CSV file and generate plotly graphs through Chainlit. This is educational and doesn't perform well.

You might want to play with the function call prompt stored in the `description` field of `PlotlyPythonAstREPLTool` to get better results.

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