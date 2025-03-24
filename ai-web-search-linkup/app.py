from typing import Any, Dict, List
import json
import os
import chainlit as cl
import tokeniser
import litellm
from linkup import LinkupClient

MAX_CONTEXT_WINDOW_TOKENS = 70000
DEFAULT_MODEL = "anthropic/claude-3-5-sonnet-20240620"

linkup_client = LinkupClient(api_key=os.environ["LINKUP_API_KEY"])

# Tool definitions
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Performs a search for user input query using Linkup sdk then returns a string of the top search results. Should be used to search real-time data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string"
                },
                "depth": {
                    "type": "string",
                    "description": "The depth of the search: 'standard' or 'deep'. Standard is faster, deep is more thorough."
                }
            },
            "required": ["query", "depth"]
        }
    }
}

# Available commands in the UI
COMMANDS = [
    {
        "id": "Search",
        "icon": "globe",
        "description": "Find on the web",
        "button": True,
        "persistent": True
    },
]


def truncate_messages(messages: List[Dict[str, Any]], max_tokens: int = MAX_CONTEXT_WINDOW_TOKENS) -> List[Dict[str, Any]]:
    """
    Truncate conversation messages to fit within token limit while preserving
    the latest user query.

    Args:
        messages: List of conversation messages
        max_tokens: Maximum allowed tokens

    Returns:
        Truncated list of messages
    """
    if not messages:
        return []

    truncated = messages.copy()

    # Always keep the latest user query
    user_query_tokens = tokeniser.estimate_tokens(truncated[-1]["content"])
    remaining_tokens = max_tokens - user_query_tokens

    # Work backwards from second-to-last message
    cutoff_index = len(truncated) - 2

    while cutoff_index > 0 and remaining_tokens > 0:
        msg_tokens = tokeniser.estimate_tokens(
            truncated[cutoff_index]["content"])

        if remaining_tokens - msg_tokens < 0:
            break

        remaining_tokens -= msg_tokens
        cutoff_index -= 1

    return truncated[cutoff_index + 1:]


async def search_web(query: str, depth: str) -> str:
    """
    Search the web using Linkup SDK

    Args:
        query: The search query string
        depth: Search depth ("standard" or "deep")

    Returns:
        Formatted search results as markdown text
    """
    try:
        search_results = linkup_client.search(
            query=query,
            depth=depth,
            output_type="searchResults",
        )

        formatted_text = "Search results:\n\n"

        for i, result in enumerate(search_results.results, 1):
            formatted_text += f"{i}. **{result.name}**\n"
            formatted_text += f"   URL: {result.url}\n"
            formatted_text += f"   {result.content}\n\n"

        return formatted_text
    except Exception as e:
        return f"Search failed: {str(e)}"


async def process_tool_calls(tool_calls: Dict, context_messages: List[Dict[str, Any]], msg: cl.Message):
    """
    Process tool calls made by the model

    Args:
        tool_calls: Dictionary of tool calls from the model
        context_messages: Conversation context
        msg: Chainlit message object for streaming response
    """
    # Show temporary "searching" message
    tmp_message = cl.Message(content="Searching the web...", author="Tool")
    await tmp_message.send()
    await cl.sleep(1)

    for _, tool_info in tool_calls.items():
        try:
            arguments = json.loads(tool_info["arguments"])

            if tool_info["name"] == "search_web":
                # Execute web search
                search_result = await search_web(
                    arguments["query"],
                    arguments["depth"]
                )

                # Add search results to conversation context
                context_messages.append({
                    "role": "user",
                    "content": search_result
                })

        except json.JSONDecodeError:
            await msg.stream_token("Error: Failed to parse tool arguments")
        except Exception as e:
            await msg.stream_token(f"Error: Tool execution failed - {str(e)}")

    # Remove temporary message
    await tmp_message.remove()

    # Generate final response with search results
    system_prompt = "Based on the information, give a comprehensive answer. At the end of your answer, list the used sources with their name and url."

    await msg.stream_token("\n\n")

    stream = await litellm.acompletion(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt}, *context_messages],
        stream=True

    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            await msg.stream_token(chunk.choices[0].delta.content)


async def run_with_tools(messages: List[Dict[str, Any]], selected_tool: str = None) -> str:
    """
    Run a conversation through Claude with function calling enabled.

    Args:
    Args:
        messages: List of conversation messages
        selected_tool: Optional tool to force using

    Returns:
        Generated response content
    """
    # Create message for streaming
    msg = cl.Message(content="", author="Claude")

    # Truncate messages to fit context window
    context_messages = truncate_messages(messages)

    # Configure tool choice
    tool_choice = "auto"
    if selected_tool:
        tool_choice = {"type": "function", "function": {"name": selected_tool}}

    # Initial response generation
    current_tool_calls = {}
    response_content = ""

    system_prompt = "You're an helpful assistant. Please provide a response to the user's query."

    # Stream the response
    try:
        stream = await litellm.acompletion(
            model=DEFAULT_MODEL,
            messages=[{"role": "system", "content": system_prompt},
                      *context_messages],
            tools=[SEARCH_TOOL],
            tool_choice=tool_choice,
            stream=True
        )

        async for chunk in stream:
            # Process text content
            if chunk.choices[0].delta.content:
                response_content += chunk.choices[0].delta.content
                await msg.stream_token(chunk.choices[0].delta.content)

            # Process tool calls
            if chunk.choices[0].delta.tool_calls:
                for tool_call in chunk.choices[0].delta.tool_calls:
                    tool_id = tool_call.index

                    # Initialize new tool call
                    if tool_id not in current_tool_calls and tool_call.function.name:
                        current_tool_calls[tool_id] = {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments or ""
                        }
                    # Append to existing tool call
                    elif tool_id in current_tool_calls:
                        current_tool_calls[tool_id]["arguments"] += tool_call.function.arguments or ""

            # Add assistant's response to context
            context_messages.append(
                {"role": "assistant", "content": response_content})

        # Send initial message
        await msg.send()

        # Process any tool calls
        if current_tool_calls:
            if len(response_content) == 0:
                # Display initial message if no response content. Can be the case when the user explicitly asks for a tool.
                response_content = "To answer this question thoroughly, I'll need to use my tools !"

                await msg.stream_token(response_content)
                await msg.update()
            await process_tool_calls(current_tool_calls, context_messages, msg)

        # Update the message with final content
        await msg.update()

        return response_content

    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        await cl.Message(content=error_msg).send()
        return error_msg


@cl.on_chat_start
async def start_chat():
    """Initialize the chat session"""

    await cl.context.emitter.set_commands(COMMANDS)

    cl.user_session.set("chat_messages", [])


@cl.on_message
async def on_message(msg: cl.Message):
    """Handle incoming user messages"""

    chat_messages = cl.user_session.get("chat_messages", [])
    chat_messages.append({"role": "user", "content": msg.content})

    # Process message with or without explicit search command
    if msg.command == "Search":
        response = await run_with_tools(chat_messages, "search_web")
    else:
        response = await run_with_tools(chat_messages)

    chat_messages.append({"role": "assistant", "content": response})
    cl.user_session.set("chat_messages", chat_messages)
