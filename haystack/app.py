import os

from datasets import load_dataset
from haystack.agents.base import Tool
from haystack.agents.conversational import ConversationalAgent
from haystack.agents.memory import ConversationSummaryMemory
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, PromptNode
from haystack.pipelines import DocumentSearchPipeline

import chainlit as cl


openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")


@cl.cache
def get_retriever():
    document_store = InMemoryDocumentStore(use_bm25=True)

    dataset = load_dataset("bilgeyucel/seven-wonders", split="train")
    document_store.write_documents(dataset)

    return BM25Retriever(document_store)


@cl.cache
def get_agent(retriever):
    pipeline = DocumentSearchPipeline(retriever)

    search_tool = Tool(
        name="seven_wonders_search",
        pipeline_or_node=pipeline,
        description="useful for when you need to answer questions about the seven wonders of the world: Colossus of Rhodes, Statue of Zeus, Great Pyramid of Giza, Mausoleum at Halicarnassus, Temple of Artemis, Lighthouse of Alexandria and Hanging Gardens of Babylon",
        output_variable="documents",
    )

    conversational_agent_prompt_node = PromptNode(
        "gpt-3.5-turbo",
        api_key=openai_api_key,
        max_length=256,
        stop_words=["Observation:"],
    )

    memory = ConversationSummaryMemory(
        conversational_agent_prompt_node,
        prompt_template="deepset/conversational-summary",
        summary_frequency=3,
    )

    agent_prompt = """
In the following conversation, a human user interacts with an AI Agent. The human user poses questions, and the AI Agent goes through several steps to provide well-informed answers.
The AI Agent must use the available tools to find the up-to-date information. The final answer to the question should be truthfully based solely on the output of the tools. The AI Agent should ignore its knowledge when answering the questions.
The AI Agent has access to these tools:
{tool_names_with_descriptions}

The following is the previous conversation between a human and The AI Agent:
{memory}

AI Agent responses must start with one of the following:

Thought: [the AI Agent's reasoning process]
Tool: [tool names] (on a new line) Tool Input: [input as a question for the selected tool WITHOUT quotation marks and on a new line] (These must always be provided together and on separate lines.)
Observation: [tool's result]
Final Answer: [final answer to the human user's question]
When selecting a tool, the AI Agent must provide both the "Tool:" and "Tool Input:" pair in the same response, but on separate lines.

The AI Agent should not ask the human user for additional information, clarification, or context.
If the AI Agent cannot find a specific answer after exhausting available tools and approaches, it answers with Final Answer: inconclusive

Question: {query}
Thought:
{transcript}
"""

    return ConversationalAgent(
        prompt_node=conversational_agent_prompt_node,
        memory=memory,
        prompt_template=agent_prompt,
        tools=[search_tool],
    )


retriever = get_retriever()
agent = get_agent(retriever)
cl.HaystackAgentCallbackHandler(agent)


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"custom-at-query-time": "Agent Step"}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_start
async def init():
    question = "What did Rhodes Statue look like?"
    await cl.Message(author="User", content=question).send()
    response = await cl.make_async(agent.run)(question)
    await cl.Message(author="Agent", content=response["answers"][0].answer).send()

    # Ask follow up questions since the agent remembers the conversation:

    # question = "When did it collapse?"
    # question = "How tall was it?"


@cl.on_message
async def answer(message: cl.Message):
    response = await cl.make_async(agent.run)(message.content)
    await cl.Message(author="Agent", content=response["answers"][0].answer).send()
