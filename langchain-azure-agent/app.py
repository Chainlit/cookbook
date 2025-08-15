from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4

from langchain_core.runnables import RunnableConfig
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_sandbox import PyodideSandboxTool

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver, CheckpointMetadata, Checkpoint, ChannelVersions

from services.document_loader import AsyncLoader
from tools.rag_search import rag_search
from tools.file_search import file_search

from services.azure_services import AzureServices

from chainlit.types import ThreadDict
import chainlit as cl
import mimetypes

# Add all supported mimetypes so the app functions on app services
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx")
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx")
mimetypes.add_type("text/plain", ".txt")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/bmp", ".bmp")
mimetypes.add_type("image/tiff", ".tiff")
mimetypes.add_type("image/heif", ".heif")
mimetypes.add_type("text/html", ".html")

checkpointer = InMemorySaver()

python_code_sandbox = PyodideSandboxTool(
    # Allow Pyodide to install python packages that
    # might be required.
    allow_net=True
)


# This function will be called every time before the node that calls LLM
def pre_model_hook(state):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=10000,
        start_on="human",
        end_on=("human", "tool"),
    )
    # You can return updated messages either under `llm_input_messages` or
    # `messages` key (see the note below)
    return {"llm_input_messages": trimmed_messages}


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
        self.msg = cl.Message(content="")

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.msg.stream_token(token)

    async def on_llm_end(self, response: str, **kwargs):
        await self.msg.send()
        self.msg = cl.Message(content="")


azure_services = AzureServices()


# Function to setup the runnable environment for the chat application
async def setup_runnable():
    """
    Sets up the runnable environment for the chat application.
    """

    # Create the prompt for the agent

    # Add knowledge of current date to the prompt
    system_prompt = "You are a helpful assistant. The current date is " + \
        datetime.now().date().strftime('%A, %Y-%m-%d')

    tools = [rag_search, python_code_sandbox]

    if cl.user_session.get("uploaded_files") is True:
        tools = [file_search]

    agent = create_react_agent(
        model=azure_services.model,
        tools=tools,
        pre_model_hook=pre_model_hook,
        prompt=system_prompt,
        checkpointer=checkpointer,
    )

    cl.user_session.set("agent", agent)


# Handler for the main chat start event
@cl.on_chat_start
async def start_chat():
    """
    Handler for the main chat start event.
    """
    # On chat start there is no thread, threads are created after first message is sent.
    cl.user_session.set("current_thread", None)
    cl.user_session.set("uploaded_files", False)

    await setup_runnable()


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
        except Exception:
            await cl.Message(
                author="System",
                content="An error occurred while reading the file. Please try again.",
            ).send()

    agent = cl.user_session.get("agent")
    await agent.ainvoke(
        {"messages": [{"role": "user", "content": message.content}]},
        config=RunnableConfig(
            configurable={"thread_id": cl.user_session.get("current_thread")},
            callbacks=[cl.LangchainCallbackHandler(), StreamHandler()]
        ),
    )


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
        loader = AsyncLoader()

        documents.extend(await loader.aload(
            file_name=element.name,
            file_mime=element.mime,
            file_path=element.path
        ))

    # If there is only a single document or chunk, directly insert that chunk into the chat history. The tool to search in uploaded files has a description that tells it to not use this tool if the information it needs is already present in the context. ChatGPT also uses this strategy.
    if len(documents) == 1:

        messages = [HumanMessage(
            content=f"File uploaded: title={documents[0].metadata.get('title', None)}, page_content={documents[0].page_content}")]

        await write_checkpoint(cl.user_session.get("current_thread"), messages)

    # Otherwise, add only the title, and vectorize the documents
    else:
        messages = [HumanMessage(
            content=(
                f"File uploaded: title={documents[0].metadata.get('title', None)}"
            )
        )]

        await azure_services.uploaded_files_vector_store.aadd_documents(documents=documents)
        await write_checkpoint(cl.user_session.get("current_thread"), messages)

    cl.user_session.set("uploaded_files", True)

    await setup_runnable()

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

    messages = [
        (HumanMessage if s["type"] == "USER_MESSAGE" else AIMessage)(
            content=s["output"])
        for s in thread["steps"]
    ]

    await write_checkpoint(thread["id"], messages)
    await setup_runnable()


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


async def write_checkpoint(
    thread_id: str,
    messages: list[AIMessage | HumanMessage],
    checkpoint_ns: str = "",
) -> str:
    """
    Persist `messages` to a checkpoint.

    Returns the generated checkpoint-id.
    """
    checkpoint_id = str(uuid4())

    checkpoint = Checkpoint(
        {
            "v": 4,
            "ts": datetime.now(timezone.utc).isoformat(),
            "id": checkpoint_id,
            "channel_versions": {"messages": "0"},
            "versions_seen": {},
            "channel_values": {"messages": list(messages)},
        }
    )

    metadata = CheckpointMetadata(
        source="import",
        step=len(messages) - 1,
        parents={},
    )

    cfg = RunnableConfig(
        configurable={
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
        }
    )

    await checkpointer.aput(
        cfg,
        checkpoint,
        metadata,
        new_versions=ChannelVersions({"messages": "0"}),
    )

    return checkpoint_id
