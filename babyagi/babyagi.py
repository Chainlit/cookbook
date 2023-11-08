#!/usr/bin/env python3
import os
import time
import logging
from collections import deque
from typing import Dict, List
import chromadb
import tiktoken as tiktoken
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import re
import openai
from openai import Client
import chainlit as cl

# default opt out of chromadb telemetry.
from chromadb.config import Settings


# Engine configuration

# Model: GPT, etc.
LLM_MODEL = os.getenv(
    "LLM_MODEL", os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")
).lower()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
assert OPENAI_API_KEY, (
    "\033[91m\033[1m"
    + "OPENAI_API_KEY environment variable is missing from .env"
    + "\033[0m\033[0m"
)

# Table config
RESULTS_STORE_NAME = os.getenv("RESULTS_STORE_NAME", os.getenv("TABLE_NAME", ""))
assert RESULTS_STORE_NAME, (
    "\033[91m\033[1m"
    + "RESULTS_STORE_NAME environment variable is missing from .env"
    + "\033[0m\033[0m"
)

# Run configuration
INSTANCE_NAME = os.getenv("INSTANCE_NAME", os.getenv("BABY_NAME", "BabyAGI"))

# Goal configuration
OBJECTIVE = os.getenv("OBJECTIVE", "")
INITIAL_TASK = os.getenv("INITIAL_TASK", os.getenv("FIRST_TASK", ""))

# Model configuration
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.0))

print("\033[95m\033[1m" + "\n*****CONFIGURATION*****\n" + "\033[0m\033[0m")
print(f"Name  : {INSTANCE_NAME}")
print(f"LLM   : {LLM_MODEL}")


# Check if we know what we are doing
assert OBJECTIVE, (
    "\033[91m\033[1m"
    + "OBJECTIVE environment variable is missing from .env"
    + "\033[0m\033[0m"
)
assert INITIAL_TASK, (
    "\033[91m\033[1m"
    + "INITIAL_TASK environment variable is missing from .env"
    + "\033[0m\033[0m"
)

if LLM_MODEL.startswith("gpt-4"):
    print(
        "\033[91m\033[1m"
        + "\n*****USING GPT-4. POTENTIALLY EXPENSIVE. MONITOR YOUR COSTS*****"
        + "\033[0m\033[0m"
    )

print("\033[94m\033[1m" + "\n*****OBJECTIVE*****\n" + "\033[0m\033[0m")
print(f"{OBJECTIVE}")

print("\033[93m\033[1m" + "\nInitial task:" + "\033[0m\033[0m" + f" {INITIAL_TASK}")

# Configure OpenAI
openai_client = Client(api_key=OPENAI_API_KEY)


async def main():
    # Results storage using local ChromaDB
    class DefaultResultsStorage:
        def __init__(self):
            logging.getLogger("chromadb").setLevel(logging.ERROR)
            # Create Chroma collection
            chroma_persist_dir = "chroma"
            chroma_client = chromadb.PersistentClient(path=chroma_persist_dir)

            metric = "cosine"
            embedding_function = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)

            # One Chroma collection per user session
            self.collection = chroma_client.get_or_create_collection(
                name=f"{RESULTS_STORE_NAME}-{cl.user_session.get('id').lower()}",
                metadata={"hnsw:space": metric},
                embedding_function=embedding_function,
            )

        def add(self, task: Dict, result: str, result_id: str):
            embeddings = None
            if (
                len(self.collection.get(ids=[result_id], include=[])["ids"]) > 0
            ):  # Check if the result already exists
                self.collection.update(
                    ids=result_id,
                    embeddings=embeddings,
                    documents=result,
                    metadatas={"task": task["task_name"], "result": result},
                )
            else:
                self.collection.add(
                    ids=result_id,
                    embeddings=embeddings,
                    documents=result,
                    metadatas={"task": task["task_name"], "result": result},
                )

        def query(self, query: str, top_results_num: int) -> List[dict]:
            count: int = self.collection.count()
            if count == 0:
                return []
            results = self.collection.query(
                query_texts=query,
                n_results=min(top_results_num, count),
                include=["metadatas"],
            )
            return [item["task"] for item in results["metadatas"][0]]

    results_storage = DefaultResultsStorage()

    # Task storage supporting only a single instance of BabyAGI
    class SingleTaskListStorage:
        def __init__(self):
            self.tasks = deque([])
            self.task_id_counter = 0

        def append(self, task: Dict):
            self.tasks.append(task)

        def replace(self, tasks: List[Dict]):
            self.tasks = deque(tasks)

        def popleft(self):
            return self.tasks.popleft()

        def is_empty(self):
            return False if self.tasks else True

        def next_task_id(self):
            self.task_id_counter += 1
            return self.task_id_counter

        def get_task_names(self):
            return [t["task_name"] for t in self.tasks]

    # Initialize tasks storage
    tasks_storage = SingleTaskListStorage()

    def limit_tokens_from_string(string: str, model: str, limit: int) -> str:
        """Limits the string to a number of tokens (estimated)."""

        try:
            encoding = tiktoken.encoding_for_model(model)
        except:
            encoding = tiktoken.encoding_for_model("gpt2")  # Fallback for others.

        encoded = encoding.encode(string)

        return encoding.decode(encoded[:limit])

    def openai_call(
        prompt: str,
        model: str = LLM_MODEL,
        temperature: float = OPENAI_TEMPERATURE,
        max_tokens: int = 100,
    ):
        while True:
            print("OpenAI call", model)
            try:
                if not model.lower().startswith("gpt-"):
                    # Use completion API
                    response = openai_client.completions.create(
                        engine=model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                    )
                    return response.choices[0].text.strip()
                else:
                    # Use 4000 instead of the real limit (4097) to give a bit of wiggle room for the encoding of roles.
                    # TODO: different limits for different models.

                    trimmed_prompt = limit_tokens_from_string(
                        prompt, model, 4000 - max_tokens
                    )

                    # Use chat completion API
                    messages = [{"role": "system", "content": trimmed_prompt}]
                    response = openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        n=1,
                        stop=None,
                    )
                    return response.choices[0].message.content.strip()
            except openai.RateLimitError:
                print(
                    "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.APITimeoutError:
                print(
                    "   *** OpenAI API timeout occurred. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.APIError:
                print(
                    "   *** OpenAI API error occurred. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.APIConnectionError:
                print(
                    "   *** OpenAI API connection error occurred. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.BadRequestError:
                print(
                    "   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            else:
                break

    def task_creation_agent(
        objective: str, result: Dict, task_description: str, task_list: List[str]
    ):
        prompt = f"""
    You are to use the result from an execution agent to create new tasks with the following objective: {objective}.
    The last completed task has the result: \n{result["data"]}
    This result was based on this task description: {task_description}.\n"""

        if task_list:
            prompt += f"These are incomplete tasks: {', '.join(task_list)}\n"
        prompt += "Based on the result, return a list of tasks to be completed in order to meet the objective. "
        if task_list:
            prompt += "These new tasks must not overlap with incomplete tasks. "

        prompt += """
    Return one task per line in your response. The result must be a numbered list in the format:

    #. First task
    #. Second task

    The number of each entry must be followed by a period. If your list is empty, write "There are no tasks to add at this time."
    Unless your list is empty, do not include any headers before your numbered list or follow your numbered list with any other output."""

        response = openai_call(prompt, max_tokens=2000)
        new_tasks = response.split("\n")
        new_tasks_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = "".join(s for s in task_parts[0] if s.isnumeric())
                task_name = re.sub(r"[^\w\s_]+", "", task_parts[1]).strip()
                if task_name.strip() and task_id.isnumeric():
                    new_tasks_list.append(task_name)

        out = [{"task_name": task_name} for task_name in new_tasks_list]
        return out

    def prioritization_agent():
        task_names = tasks_storage.get_task_names()
        bullet_string = "\n"

        prompt = f"""
    You are tasked with prioritizing the following tasks: {bullet_string + bullet_string.join(task_names)}
    Consider the ultimate objective of your team: {OBJECTIVE}.
    Tasks should be sorted from highest to lowest priority, where higher-priority tasks are those that act as pre-requisites or are more essential for meeting the objective.
    Do not remove any tasks. Return the ranked tasks as a numbered list in the format:

    #. First task
    #. Second task

    The entries must be consecutively numbered, starting with 1. The number of each entry must be followed by a period.
    Do not include any headers before your ranked list or follow your list with any other output."""

        response = openai_call(prompt, max_tokens=2000)
        if not response:
            print(
                "Received empty response from priotritization agent. Keeping task list unchanged."
            )
            return
        new_tasks = response.split("\n") if "\n" in response else [response]
        new_tasks_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = "".join(s for s in task_parts[0] if s.isnumeric())
                task_name = re.sub(r"[^\w\s_]+", "", task_parts[1]).strip()
                if task_name.strip():
                    new_tasks_list.append({"task_id": task_id, "task_name": task_name})

        return new_tasks_list

    # Execute a task based on the objective and five previous tasks
    def execution_agent(objective: str, task: str) -> str:
        """
        Executes a task based on the given objective and previous context.

        Args:
            objective (str): The objective or goal for the AI to perform the task.
            task (str): The task to be executed by the AI.

        Returns:
            str: The response generated by the AI for the given task.

        """

        context = context_agent(query=objective, top_results_num=5)
        prompt = f"Perform one task based on the following objective: {objective}.\n"
        if context:
            prompt += "Take into account these previously completed tasks:" + "\n".join(
                context
            )
        prompt += f"\nYour task: {task}\nResponse:"
        return openai_call(prompt, max_tokens=2000)

    # Get the top n completed tasks for the objective
    def context_agent(query: str, top_results_num: int):
        """
        Retrieves context for a given query from an index of tasks.

        Args:
            query (str): The query or objective for retrieving context.
            top_results_num (int): The number of top results to retrieve.

        Returns:
            list: A list of tasks as context for the given query, sorted by relevance.

        """
        results = results_storage.query(query=query, top_results_num=top_results_num)
        return results

    # Add the initial task if starting new objective
    initial_task = {
        "task_id": tasks_storage.next_task_id(),
        "task_name": INITIAL_TASK,
    }
    tasks_storage.append(initial_task)

    tasklist = cl.TaskList()
    for task in tasks_storage.tasks:
        await tasklist.add_task(cl.Task(title=task["task_name"]))
    await tasklist.send()

    loop = True
    while loop:
        # As long as there are tasks in the storage...
        if not tasks_storage.is_empty():
            # Step 1: Pull the first incomplete task
            task = tasks_storage.popleft()
            message_id = await cl.Message(
                content=f"## Task\n\n{task['task_name']}"
            ).send()
            for t in tasklist.tasks:
                if t.title == task["task_name"]:
                    t.status = cl.TaskStatus.RUNNING
                    t.forId = message_id
            await tasklist.send()

            # Send to execution function to complete the task based on the context

            async_execution_agent = cl.make_async(execution_agent)
            result = await async_execution_agent(OBJECTIVE, str(task["task_name"]))
            for t in tasklist.tasks:
                if t.status == cl.TaskStatus.RUNNING:
                    t.status = cl.TaskStatus.DONE
            await tasklist.send()
            await cl.Message(content=f"## Result\n\n{result}").send()

            # Step 2: Enrich result and store in the results storage
            # This is where you should enrich the result if needed
            enriched_result = {"data": result}
            # extract the actual result from the dictionary
            # since we don't do enrichment currently
            # vector = enriched_result["data"]

            result_id = f"result_{task['task_id']}"

            results_storage.add(task, result, result_id)

            await cl.Message(content=f"Creating new tasks...").send()

            # Step 3: Create new tasks and re-prioritize task list
            # only the main instance in cooperative mode does that
            async_task_creation_agent = cl.make_async(
                task_creation_agent, cancellable=True
            )
            new_tasks = await async_task_creation_agent(
                OBJECTIVE,
                enriched_result,
                task["task_name"],
                tasks_storage.get_task_names(),
            )

            await cl.Message(content=f"Re-prioritizing the task list...").send()

            # print('Adding new tasks to task_storage')
            for new_task in new_tasks:
                new_task.update({"task_id": tasks_storage.next_task_id()})
                # print(str(new_task))
                # await cl.Message(content=str(new_task)).send()
                tasks_storage.append(new_task)

            async_prioritization_agent = cl.make_async(
                prioritization_agent, cancellable=True
            )
            prioritized_tasks = await async_prioritization_agent()
            if prioritized_tasks:
                tasks_storage.replace(prioritized_tasks)
                tasklist.tasks = [
                    t for t in tasklist.tasks if t.status != cl.TaskStatus.READY
                ]
                for task in prioritized_tasks:
                    await tasklist.add_task(cl.Task(title=task["task_name"]))
                await tasklist.send()

            # Sleep a bit before checking the task list again
            await cl.sleep(1)
        else:
            print("Done.")
            loop = False


@cl.on_chat_start
async def on_chat_start():
    print("New BabyAGI session started.")
    await main()
