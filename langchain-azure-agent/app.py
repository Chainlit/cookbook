from datetime import datetime
import os
from typing import Dict, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from tools.rag_search import rag_search
from tools.web_search import web_search
from tools.uploaded_files_search import uploaded_files_search

from services.azure_services import AzureServices

from chainlit.types import ThreadDict
import chainlit as cl
import mimetypes


# Add all supported mimetypes so the app functions on app services
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"
)
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"
)
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"
)
mimetypes.add_type("text/plain", ".txt")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/bmp", ".bmp")
mimetypes.add_type("image/tiff", ".tiff")
mimetypes.add_type("image/heif", ".heif")
mimetypes.add_type("text/html", ".html")


text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4o",
    chunk_size=5000,
    chunk_overlap=500,
)

azure_services = AzureServices()

DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_API_KEY = os.getenv("DOCUMENT_INTELLIGENCE_API_KEY")


# Callback handler for handling streaming responses from the language model
class StreamHandler(BaseCallbackHandler):
    """
    A callback handler for handling streaming responses from the language model.

    Attributes:
        msg (cl.Message): The message object used for streaming the response.

    Methods:
        on_llm_new_token: Called when a new token is received from the language model.
        on_llm_end: Called when the streaming response from the language model ends.
    """

    def __init__(self):
        self.msg = None

    async def on_llm_new_token(self, token: str, **kwargs):
        if not token:
            return

        if self.msg is None:
            self.msg = cl.Message(content="", author="Assistant")

        await self.msg.stream_token(token)

    async def on_llm_end(self, response: str, **kwargs):
        if self.msg:
            await self.msg.send()
        self.msg = None


# Function to setup the runnable environment for the chat application
async def setup_runnable(memory: ConversationSummaryBufferMemory):
    """
    Sets up the runnable environment for the chat application.
    """

    # Create the prompt for the agent

    # Add knowledge of current date to the prompt
    system_prompt = (
        "You are a helpful assistant. The current date is "
        + datetime.now().date().strftime("%A, %Y-%m-%d")
    )

    # Create the chat prompt template, the ordering of the placeholders is important, taken from: https://smith.langchain.com/hub/hwchase17/openai-tools-agent
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent_tools = [rag_search, web_search]

    if cl.user_session.get("uploaded_files") is True:
        agent_tools = [uploaded_files_search]

    # Create the OpenAI Tools agent using the specified model, tools, and prompt
    agent = create_tool_calling_agent(azure_services.model, agent_tools, prompt)

    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(
        agent=agent, tools=agent_tools, memory=memory, max_iterations=5
    )

    # Set the agent executor in the user session
    cl.user_session.set("agent_executor", agent_executor)


# Handler for the main chat start event
@cl.on_chat_start
async def start_chat():
    """
    Handler for the main chat start event.
    """
    # On chat start there is no thread, threads are created after first message is sent.
    cl.user_session.set("current_thread", None)
    cl.user_session.set("uploaded_files", False)

    conversation_summary_memory = ConversationSummaryBufferMemory(
        llm=azure_services.model,
        max_token_limit=4000,
        memory_key="chat_history",
        return_messages=True,
    )
    await setup_runnable(conversation_summary_memory)


# Handler for the main message event
@cl.on_message
async def chat(message: cl.Message):
    """
    Handler for the main message event.
    This function is the main entry point for processing user messages in the chat application.
    It handles both regular messages and file uploads.
    """
    cl.user_session.set("current_thread", message.thread_id)
    # If the message contains file elements, start the file loading process
    if message.elements:
        try:
            await file_loader(message)
        except Exception as e:
            await cl.Message(
                author="System",
                content="An error occurred while reading the file. Please try again.",
            ).send()

    # Get the agent executor from the user session
    agent_executor: AgentExecutor = cl.user_session.get("agent_executor")

    # Invoke the agent with the user message as input
    try:
        await agent_executor.ainvoke(
            {"input": message.content},
            {"callbacks": [cl.AsyncLangchainCallbackHandler(), StreamHandler()]},
        )
    except Exception as e:
        await cl.Message(
            author="System",
            content="An error occurred while processing the message. Please try again.",
        ).send()


# Function to handle file loading
@cl.step(type="tool")
async def file_loader(message: cl.Message):
    """
    This function processes the files uploaded by the user for further use by the chat application.
    The processed documents are then added to the conversation memory or a vector store
    and then splits the content into manageable chunks using a text splitter.
    It uses the Azure AI Document Intelligence service to extract content from the files.
    """

    documents = []
    for element in message.elements:
        loader = AzureAIDocumentIntelligenceLoader(
            api_endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
            api_key=DOCUMENT_INTELLIGENCE_API_KEY,
            file_path=element.path,
            api_model="prebuilt-layout",
            mode="markdown",
        )

        docs = await cl.make_async(loader.load)()

        split_docs = await text_splitter.atransform_documents(docs)

        for doc in split_docs:
            doc.metadata["thread_id"] = message.thread_id
            doc.metadata["title"] = element.name
            documents.append(doc)

    # If there is only a single document or chunk, directly insert that chunk into the chat history. The tool to search in uploaded files has a description that tells it to not use this tool if the information it needs is already present in the context. ChatGPT also uses this strategy.
    if len(documents) == 1:
        single_doc = documents[0]

        # Insert the document's content into the chat history as a "context" field
        conversation_summary_memory = cl.user_session.get("agent_executor").memory

        conversation_summary_memory.chat_memory.add_ai_message(
            f"context: page_content={single_doc.page_content}, "
            f"title={single_doc.metadata.get('title', None)}"
        )

        await setup_runnable(conversation_summary_memory)
    else:
        await azure_services.uploaded_files_vector_store.aadd_documents(documents)

    cl.user_session.set("uploaded_files", True)

    await setup_runnable(cl.user_session.get("agent_executor").memory)
    await cl.Message(
        author="System",
        content="Done reading and memorizing files.",
    ).send()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """
    This function is triggered when the chat application is resumed after being paused.
    It initializes the ConversationSummaryBufferMemory with the history from the previous session.
    """

    cl.user_session.set("current_thread", thread["id"])

    # Create a new ConversationSummaryBufferMemory with the specified parameters
    conversation_summary_memory = ConversationSummaryBufferMemory(
        llm=azure_services.model,
        max_token_limit=4000,
        memory_key="chat_history",
        return_messages=True,
    )

    # Retrieve the root messages from the thread
    root_messages = [m for m in thread["steps"] if m["parentId"] is None]
    # Iterate over the root messages
    for message in root_messages:
        # Check the type of the message
        if message["type"] == "USER_MESSAGE":
            # Add user message to the chat memory
            conversation_summary_memory.chat_memory.add_user_message(message["output"])
        else:
            # Add AI message to the chat memory
            conversation_summary_memory.chat_memory.add_ai_message(message["output"])

    # Call the setup_runnable function to continue the chat application
    await setup_runnable(conversation_summary_memory)


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    """
    This function is an OAuth callback handler.
    It is triggered when the user authorizes the application with a third-party provider.
    It receives the provider ID, token, raw user data, and default user as input parameters.
    It returns an optional User object.
    """
    return default_user


@cl.on_chat_end
async def on_chat_end():
    """
    This function is called when a chat ends.
    It sets the current_thread value in the user session to None.
    """
    cl.user_session.set("current_thread", None)
