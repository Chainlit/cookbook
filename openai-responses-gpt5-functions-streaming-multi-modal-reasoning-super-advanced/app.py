"""
Chainlit + OpenAI Integration with Local Python Execution

Simplified version with local Python executor instead of OpenAI's code interpreter
"""

import os
import json
import base64
from typing import List, Dict, Any, Optional

from openai import AsyncOpenAI
import chainlit as cl
from chainlit.input_widget import Select, Switch
import os, pathlib, shutil

# Import our custom tools
from tools import (
    build_tools, 
    call_function_tool, 
    show_tool_progress, 
    show_reasoning_summary
)

# ─────────────────── OpenAI Client Setup ────────────────────────────────────
cl.instrument_openai()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_ITER = 20
DEV_PROMPT = "Talk in Ned Flanders style. You are a helpful assistant with access to local Python execution, web search, image generation, file search, and file upload capabilities. You can upload files to a persistent Python workspace and analyze them with code. IMPORTANT: When you see function calls for 'upload_file_to_workspace' or 'list_workspace_files' in the conversation history, acknowledge what files were uploaded or are available. Always check your recent function call results to understand what the user has done. Use tools when needed."
# ─────────────────── Session Management ─────────────────────────────────────
@cl.on_chat_start
async def _start():
    """Initialize chat session with settings and optional file upload"""
    settings = await cl.ChatSettings([
        Select(
            id="reasoning_effort", 
            label="Reasoning Level", 
            values=["minimal", "low", "medium", "high"], 
            initial_index=1
        ),
        Switch(id="show_reasoning", label="Show Reasoning Summary", initial=True),
        Switch(id="show_conversation_history", label="Show Conversation History", initial=True),
        Switch(id="show_tool_execution", label="Show Tool Execution Details", initial=True),
    ]).send()

    cl.user_session.set("settings", settings)
    cl.user_session.set("full_conversation_history", [])
    cl.user_session.set("previous_response_id", None)
    cl.user_session.set("tool_results", {})
    cl.user_session.set("vector_store_id", None)
    cl.user_session.set("dev_prompt", DEV_PROMPT)
    # Ask about file upload for search capabilities
    upload_choice = await cl.AskActionMessage(
        content="Would you like to upload files for search capabilities?",
        actions=[
            cl.Action(name="upload", label="Upload files", payload={"value": "upload"}),
            cl.Action(name="skip", label="Skip", payload={"value": "skip"}),
        ],
    ).send()

    if upload_choice and upload_choice.get("value") == "upload":
        files = await cl.AskFileMessage(
            content="Upload files to search through:",
            accept=["text/plain", "application/pdf", ".txt", ".md", ".py", ".js", ".html", ".css"],
            max_files=10,
            timeout=180,
        ).send()

        if files and len(files) > 0:
            try:
                # Create vector store for file search
                vector_store = await client.vector_stores.create(name="Chat Files")
                uploaded_files = []
                
                for file in files:
                    uploaded_file = await client.files.create(
                        file=file.content, 
                        purpose="file-search"
                    )
                    uploaded_files.append(uploaded_file.id)
                
                await client.vector_stores.files.create_many(
                    vector_store_id=vector_store.id, 
                    file_ids=uploaded_files
                )
                
                cl.user_session.set("vector_store_id", vector_store.id)
                await cl.Message(
                    f"Uploaded {len(files)} files for search!", 
                    author="System"
                ).send()
                
            except Exception as e:
                await cl.Message(f"Error uploading files: {e}", author="System").send()
    else:
        await cl.Message(
            "Continuing without file upload. All features are ready including local Python execution!", 
            author="System"
        ).send()

    # Build a per-chat workspace under .files/{session_id}/pyws
    session_id = cl.user_session.get("id")  # unique per chat
    base_files_dir = os.path.join(os.getcwd(), ".files", session_id)
    ws_dir = os.path.join(base_files_dir, "pyws")
    os.makedirs(ws_dir, exist_ok=True)

    cl.user_session.set("python_workspace_dir", ws_dir)
    await cl.Message(f"Using per-chat workspace: `{ws_dir}`", author="System").send()


@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates"""
    cl.user_session.set("settings", settings)

@cl.on_chat_end
def _cleanup():
    ws_dir = cl.user_session.get("python_workspace_dir")
    if ws_dir and os.path.isdir(ws_dir):
        try:
            shutil.rmtree(ws_dir)
        except Exception:
            pass

# ─────────────────── Core GPT Interaction ───────────────────────────────────
async def _ask_gpt(input_data, prev_id=None):
    """
    Send request to OpenAI API and handle streaming response
    
    Args:
        input_data: Input for the API call - can be a string, list of messages, or full conversation history
        prev_id: Previous response ID for continuation
        
    Returns:
        Tuple of (response_id, function_calls)
    """
    # Get user settings
    settings = cl.user_session.get("settings", {})
    vector_store_id = cl.user_session.get("vector_store_id")
    tools = build_tools(vector_store_id)

    reasoning_effort = settings.get("reasoning_effort", "low")
    show_reasoning = settings.get("show_reasoning", True)

    # Configure reasoning
    reasoning_config = {"effort": reasoning_effort}
    if show_reasoning:
        reasoning_config["summary"] = "auto"

    # Handle different input types
    if isinstance(input_data, list) and len(input_data) > 0 and isinstance(input_data[0], dict):
        # This is a list of messages for the current turn
        api_input = input_data
    else:
        # Single input (string or multimodal)
        api_input = input_data
    dev_input = []
    if not prev_id:
        dev_input.append({
            "role": "developer",  # or "system"
            "content": cl.user_session.get("dev_prompt") or DEV_PROMPT,
        })
    print(dev_input + api_input)
    # Make API call with streaming
    stream = await client.responses.create(
        model="gpt-5-mini",
        reasoning=reasoning_config,
        input=dev_input + api_input,
        instructions=(
            "You are a helpful, neutral assistant. Use the execute_python_code function "
            "when you need to run Python code, create visualizations, or perform data analysis. "
            "The function runs code locally and can generate files like plots, CSVs, etc. "
            "Always explain what the code does before executing it. "
            "Pay attention to any function call results in the conversation history - these show what actions have been taken."
        ),
        stream=True,
        store=True,
        tools=tools,
        tool_choice="auto",
        **({"previous_response_id": prev_id} if prev_id else {}),
    )

    # Initialize response tracking
    ans = cl.Message(author="Assistant", content="")
    await ans.send()
    
    calls = []
    resp_id = None
    assistant_text = ""
    reasoning_text = ""
    
    # Track function call streaming
    streaming_code_message = None
    current_code = ""

    # Process streaming response
    async for ev in stream:
        if ev.type == "response.created":
            resp_id = ev.response.id
            
        elif ev.type == "response.completed":
            # Response completed
            pass

        # Tool progress tracking
        elif ev.type == "response.web_search_call.in_progress":
            if settings.get("show_tool_execution", True):
                await show_tool_progress("web_search_call", "in_progress")
        elif ev.type == "response.web_search_call.searching":
            if settings.get("show_tool_execution", True):
                await show_tool_progress("web_search_call", "searching")
        elif ev.type == "response.web_search_call.completed":
            if settings.get("show_tool_execution", True):
                await show_tool_progress("web_search_call", "completed")

        elif ev.type == "response.image_generation_call.in_progress":
            if settings.get("show_tool_execution", True):
                await show_tool_progress("image_generation_call", "in_progress")
        elif ev.type == "response.image_generation_call.generating":
            if settings.get("show_tool_execution", True):
                await show_tool_progress("image_generation_call", "generating")
        elif ev.type == "response.image_generation_call.completed":
            if settings.get("show_tool_execution", True):
                await show_tool_progress("image_generation_call", "completed")

        # Reasoning summary streaming
        elif ev.type == "response.reasoning_summary_text.delta":
            reasoning_text += ev.delta

        # Function calls
        elif ev.type == "response.output_item.added" and getattr(ev.item, "type", "") == "function_call":
            calls.append({
                "id": ev.item.id,
                "call_id": ev.item.call_id,
                "name": ev.item.name,
                "arguments": ""
            })
            
            # If this is a Python code execution call, start streaming display
            if ev.item.name == "execute_python_code":
                streaming_code_message = cl.Message(
                    author="Code Generator",
                    content="**Python Code Being Generated:**\n```python\n\n```"
                )
                await streaming_code_message.send()
                current_code = ""
                
        elif ev.type == "response.function_call_arguments.delta":
            # Find the call and append arguments
            for call in calls:
                if call["id"] == ev.item_id:
                    call["arguments"] += ev.delta
                    
                    # If this is Python code, stream the code generation
                    if call["name"] == "execute_python_code" and streaming_code_message:
                        try:
                            # Try to parse the current arguments to extract code
                            # We might have incomplete JSON, so we need to handle this carefully
                            current_args_str = call["arguments"]
                            
                            # Try to find the code field in the JSON string
                            if '"code":"' in current_args_str:
                                # Extract everything after "code":"
                                code_start = current_args_str.find('"code":"') + 8
                                code_part = current_args_str[code_start:]
                                
                                # Find the end of the code string (look for unescaped quote)
                                # This is a simple approach - we'll look for the pattern
                                code_end = len(code_part)
                                if '"}' in code_part:
                                    code_end = code_part.find('"}')
                                elif '",' in code_part:
                                    code_end = code_part.find('",')
                                
                                new_code = code_part[:code_end]
                                
                                # Unescape the JSON string
                                new_code = new_code.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                                
                                if new_code != current_code:
                                    current_code = new_code
                                    streaming_code_message.content = f"**Python Code Being Generated:**\n```python\n{current_code}\n```"
                                    await streaming_code_message.update()
                        except Exception as e:
                            # If parsing fails, just continue - we'll get more data
                            pass
                    break

        # Assistant text streaming
        elif ev.type == "response.output_text.delta":
            assistant_text += ev.delta
            await ans.stream_token(ev.delta)

    await ans.update()

    # Display reasoning summary if available
    if reasoning_text.strip() and settings.get("show_reasoning", True):
        await show_reasoning_summary(reasoning_text)

    # Update conversation history
    if assistant_text.strip():
        full_history = cl.user_session.get("full_conversation_history", [])
        full_history.append({"role": "assistant", "content": assistant_text})
        cl.user_session.set("full_conversation_history", full_history)

    return resp_id, calls


# ─────────────────── Message Handling ───────────────────────────────────────
@cl.on_message
async def _on_msg(m: cl.Message):
    """
    Handle incoming messages with support for text, images, and file uploads
    
    Args:
        m: Chainlit message object
    """
    full_history = cl.user_session.get("full_conversation_history", [])

    # Initialize conversation if empty
    if not full_history:
        full_history.append({
            "role": "developer", 
            "content": cl.user_session.get("dev_prompt") or DEV_PROMPT
        })

    # Handle file uploads by converting them to function calls
    uploaded_files = []
    if m.elements:
        for element in m.elements:
            # Handle file uploads
            if hasattr(element, 'path') and hasattr(element, 'name') and not (element.mime and element.mime.startswith("image/")):
                try:
                    # Read the file content
                    with open(element.path, 'rb') as f:
                        file_content = f.read()
                    
                    # Convert to base64 for the function call
                    import base64
                    content_b64 = base64.b64encode(file_content).decode('utf-8')
                    
                    # Create a function call for file upload
                    uploaded_files.append({
                        'filename': element.name,
                        'content_b64': content_b64,
                        'size': len(file_content)
                    })
                except Exception as e:
                    await cl.Message(
                        content=f"Failed to process uploaded file {element.name}: {str(e)}",
                        author="System"
                    ).send()

    # Handle multimodal input (text + images)
    image_count = 0
    if m.elements:
        content = [{"type": "input_text", "text": m.content}]
        
        for element in m.elements:
            if element.mime and element.mime.startswith("image/"):
                if hasattr(element, "path") and element.path:
                    # Read image file and encode as base64
                    with open(element.path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                        content.append({
                            "type": "input_image", 
                            "image_url": f"data:{element.mime};base64,{encoded_string}"
                        })
                        image_count += 1
                elif element.url:
                    content.append({"type": "input_image", "image_url": element.url})
                    image_count += 1
        
        # Only use multimodal format if we have images
        if image_count > 0:
            current_input = [{"role": "user", "content": content}]
            history_content = f"{m.content} [+ {image_count} image(s)]"
        else:
            current_input = [{"role": "user", "content": m.content}]
            history_content = m.content
    else:
        current_input = [{"role": "user", "content": m.content}]
        history_content = m.content

    # Get previous response ID for continuation
    prev_response_id = cl.user_session.get("previous_response_id")

    # Process any file uploads first and enhance the user message
    upload_info = []
    for file_info in uploaded_files:
        # Execute the upload
        upload_call = {
            "id": f"upload_{file_info['filename']}",
            "call_id": f"upload_{file_info['filename']}_call",
            "name": "upload_file_to_workspace",
            "arguments": json.dumps({
                "filename": file_info['filename'],
                "content": file_info['content_b64']
            })
        }
        
        await call_function_tool(upload_call, full_history)
        
        # After upload, automatically list files  
        list_files_call = {
            "id": f"list_after_upload_{file_info['filename']}",
            "call_id": f"list_after_upload_{file_info['filename']}_call", 
            "name": "list_workspace_files",
            "arguments": "{}"
        }
        
        await call_function_tool(list_files_call, full_history)
        
        # Add info about what was uploaded
        upload_info.append(f"{file_info['filename']} ({file_info['size']:,} bytes)")

    # Enhance the user message to inform the AI about uploads
    # Add file upload info to history
    if uploaded_files:
        additional_note = f"\n\nNote: I just uploaded {len(uploaded_files)} file(s) to your Python workspace: {', '.join([f['filename'] for f in uploaded_files])}. These files are now available for analysis."
        history_content += additional_note

    # Update conversation history
    full_history.append({"role": "user", "content": history_content})
    cl.user_session.set("full_conversation_history", full_history)
    enhanced_content = m.content
    if upload_info:
        additional_note = f"\n\nNote: I just uploaded {len(uploaded_files)} file(s) to your Python workspace: {', '.join([f['filename'] for f in uploaded_files])}. These files are now available for analysis."
        enhanced_content += additional_note

    # Update the current input with enhanced message
    if image_count > 0:
        # Update the text part of multimodal content
        for item in content:
            if item["type"] == "input_text":
                item["text"] = enhanced_content
        current_input = [{"role": "user", "content": content}]
    else:
        current_input = [{"role": "user", "content": enhanced_content}]

    # Handle multiple iterations for function calls
    for iteration in range(MAX_ITER):
        resp_id, calls = await _ask_gpt(current_input, prev_response_id)
        
        if not calls:
            # No function calls, we're done
            break

        # Get settings for this iteration
        settings = cl.user_session.get("settings", {})
        
        # Process function calls
        for call in calls:
            if settings.get("show_tool_execution", True):
                await show_tool_progress("python_execution", "in_progress")
            
            await call_function_tool(call, full_history)
            
            if settings.get("show_tool_execution", True):
                await show_tool_progress("python_execution", "completed")

        # Prepare function results for next iteration
        tool_results = cl.user_session.get("tool_results", {})
        current_input = [
            {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": tool_results[call["call_id"]]
            }
            for call in calls
        ]
        prev_response_id = resp_id

    # Update session state
    cl.user_session.set("full_conversation_history", full_history)
    cl.user_session.set("previous_response_id", resp_id)

    # Show conversation history if enabled
    settings = cl.user_session.get("settings", {})
    if settings.get("show_conversation_history", True):
        await show_full_conversation([{"role": "user", "content": m.content}], full_history)


# ─────────────────── Debug and Utilities ────────────────────────────────────
@cl.step(type="tool")
async def show_full_conversation(current_message: List[Dict], full_history: List[Dict]):
    """
    Display full conversation history for debugging
    
    Args:
        current_message: Current message that triggered this
        full_history: Complete conversation history
    """
    s = cl.context.current_step
    s.name = "Full Conversation History"
    s.input = current_message

    # Format history for display
    formatted_history = []
    for msg in full_history:
        if isinstance(msg, dict):
            role = msg.get("role")
            if role in ("system", "user", "assistant", "developer"):
                formatted_history.append({
                    "role": role, 
                    "content": msg["content"]
                })
            elif role == "function" or msg.get("name"):
                formatted_history.append({
                    "role": "function",
                    "name": msg.get("name", "unknown_function"),
                    "content": msg["content"],
                    "tool_call_id": msg.get("tool_call_id", "unknown_id"),
                })
            else:
                formatted_history.append(msg)
        else:
            formatted_history.append(msg)

    s.output = formatted_history
    s.language = "json"
    return formatted_history


if __name__ == "__main__":
    # Entry point for running the Chainlit app
    import chainlit as cl
    cl.run()