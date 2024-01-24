---
title: 'Chainlit BabyAGI Integration Demo'
tags: ['babyagi', 'integration', 'chainlit']
---

# Chainlit BabyAGI Integration Demo

This repository demonstrates the integration of Chainlit with BabyAGI, an autonomous agent framework. The integration showcases how Chainlit can be used to enhance observability and interaction with AI agents.

## High-Level Description

The `babyagi.py` script initializes an instance of BabyAGI with a specific objective and a set of tasks to accomplish. It uses OpenAI's API to process and generate responses for each task. The script also includes functionality to prioritize tasks, store results, and generate new tasks based on previous outcomes. The Chainlit framework is used to provide a user interface for interacting with the agent, allowing users to start sessions, receive updates on task statuses, and view results.

## Quickstart

### Prerequisites

- Python ≥ 3.9
- An OpenAI API key
- Chainlit installed

### Setup and Run

1. **Install Dependencies:**

Install the required Python packages.

```shell
pip install -r requirements.txt
```

2. **Environment Configuration:**

Copy the example environment file and set the required environment variables.

```shell
cp .env.example .env
```
Edit .env to include your OPENAI_API_KEY and OBJECTIVE


3. **Run the Demo:**

Execute the script to start the Chainlit UI in a browser window.

```shell
chainlit run babyagi.py
```

## Function Definitions

- `main()`: The main coroutine that initializes the results storage, task storage, and starts the task execution loop.
- `DefaultResultsStorage`: A class to handle the storage of task results using ChromaDB.
- `SingleTaskListStorage`: A class to manage the list of tasks for BabyAGI.
- `openai_call()`: A function to make calls to the OpenAI API and handle different types of errors.
- `task_creation_agent()`: A function that generates new tasks based on the results of executed tasks and the overall objective.
- `prioritization_agent()`: A function that prioritizes tasks based on their relevance to the objective.
- `execution_agent()`: A function that executes a given task using the OpenAI API.
- `context_agent()`: A function that retrieves context for a given query from the results storage.

## Credits

The code is based on the [BabyAGI](https://github.com/yoheinakajima/babyagi/) repository by [Yohei Nakajima](https://twitter.com/yoheinakajima).
