Title: Human-In-The-Loop Tool
Tags: [human-interaction]


## Ask Human

The `Ask Human` script is designed to integrate human input into automated workflows. It allows a Python application to pause its execution and query the end-user for additional information or guidance, effectively creating a human-in-the-loop system.

### Key Features

- Utilizes `cl.AskUserMessage()` to pause the agent's execution and request input from the user.
- Seamlessly integrates with the `langchain` library to enhance language model chains with human input.
- Supports both synchronous and asynchronous execution for flexibility in different runtime environments.

### Quickstart

To get started with the `Ask Human` tool, follow these steps:

1. Ensure you have the `chainlit` and `langchain` libraries installed in your Python environment.
2. Import the necessary classes from `langchain` and `chainlit`.
3. Define the `HumanInputChainlit` class, which inherits from `BaseTool`, to create the human input tool.
4. Set up the `start` function with the necessary language model and tools.
5. Implement the `main` function to handle incoming messages and execute the agent with the human input tool.

Here's a simple example of how to define the `HumanInputChainlit` tool:
    
```python
class HumanInputChainlit(BaseTool):
"""Tool that adds the capability to ask user for input."""

name = "human"
description = (
"You can ask a human for guidance when you think you "
"got stuck or you are not sure what to do next. "
"The input should be a question for the human."
)

def run(self, query: str, run_manager=None) -> str:
"""Use the Human input tool."""
res = run_sync(cl.AskUserMessage(content=query).send())
return res["content"]

async def _arun(self, query: str, run_manager=None) -> str:
"""Use the Human input tool."""
res = await cl.AskUserMessage(content=query).send()
return res["output"]
```

To use the `Ask Human` tool in your application, simply instantiate the `HumanInputChainlit` class and include it in your agent's toolset.

For a visual demonstration, refer to the following asset which may include a screenshot or GIF illustrating the tool in action:

![Human-In-The-Loop Tool Demonstration](https://github.com/Chainlit/cookbook/assets/16107237/5352b277-4eef-4716-a4f4-233864bf696e)