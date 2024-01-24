---
title: 'BigQuery Agent with Chainlit'
tags: ['bigquery', 'chainlit']
---

# BigQuery Agent with Chainlit

This repository contains a Chainlit application that acts as an interface between users and Google BigQuery. It leverages OpenAI's language model to generate SQL queries from natural language questions, execute them on BigQuery, and then analyze and explain the results in a user-friendly manner.

## How it Works

The `app.py` script is composed of several asynchronous functions that work together to:

1. **Generate SQL Query (`gen_query`)**: Takes a natural language question from the user and generates an SQL query using OpenAI's language model.
2. **Execute Query (`execute_query`)**: Runs the generated SQL query on Google BigQuery and retrieves the results in a Markdown table format.
3. **Analyze Results (`analyze`)**: Analyzes the query results and provides a concise explanation of the findings.
4. **Chain Steps (`chain`)**: Orchestrates the above steps to process a user's question and return an analysis of the BigQuery data.

## Quickstart

### Prerequisites

- Python 3.9 or higher
- Chainlit installed
- Google Cloud SDK installed
- OpenAI API key
- Google Cloud credentials with access to BigQuery

### Setup and Run

1. **Install Dependencies:**

Install the required Python packages.

```shell
pip install chainlit google-cloud-bigquery openai
```

2. **Google Cloud Authentication:**

Authenticate with Google Cloud to access BigQuery.

```shell
gcloud auth application-default login
```


3. **Environment Configuration:**

Set the necessary environment variables for OpenAI and BigQuery.


4. **Run the Application:**

Start the Chainlit application.

```shell
chainlit run app.py
```

## Code Definitions

- `gen_query`: Asynchronous function that generates an SQL query from a human question using OpenAI's language model.
- `execute_query`: Asynchronous function that executes the SQL query on BigQuery and formats the results as a Markdown table.
- `analyze`: Asynchronous function that analyzes the BigQuery results and provides an explanation.
- `chain`: Asynchronous function that orchestrates the flow from receiving a human question to providing an analysis of the data.
- `main`: Entry point for messages received from the user, initiating the chain of steps.
- `take_action`: Callback function for any actions taken from the Chainlit UI, such as contacting a shipping carrier.
- `auth_callback`: Callback function for handling OAuth authentication with Google.

This application streamlines the process of querying BigQuery and interpreting results, making data analysis more accessible to users without SQL expertise. Here's a quickstart: [get started video](https://github.com/Chainlit/chainlit/assets/13104895/cbcb8078-ab4d-4e4c-8e4e-7aaa51ca1fd0).
