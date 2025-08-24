"""
Custom tools and functions for Chainlit + OpenAI integration
Includes local Python executor and other utility functions
"""

import json
import subprocess
import sys
import tempfile
import os
import pathlib
import base64
from typing import List, Dict, Any, Optional, Tuple
import chainlit as cl


class LocalPythonExecutor:
    """Execute Python code locally and return results with file attachments"""
    
    def __init__(self):
        # Use a persistent workspace directory instead of temporary
        ws = cl.user_session.get("python_workspace_dir")
        if not ws:
            # Fallback to .files/<session_id>/pyws to ensure isolation,
            # and finally to the old persistent folder if nothing else.
            session_id = cl.user_session.get("id") or "default"
            ws = os.path.join(os.getcwd(), ".files", session_id, "pyws")
        self.workspace_dir = ws
        os.makedirs(self.workspace_dir, exist_ok=True)
        self.output_files = []
    
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code locally and capture output, errors, and generated files
        
        Args:
            code: Python code to execute
            
        Returns:
            Dict containing stdout, stderr, return_code, and generated files
        """
        # Create a temporary Python file in the workspace
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.workspace_dir)
        
        # Track files before execution (in the persistent workspace)
        initial_files = set(os.listdir(self.workspace_dir))
        
        # Modify the code to work in the persistent workspace and list existing files
        enhanced_code = f"""
import sys
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Change to workspace directory (using raw string to handle Windows paths)
os.chdir(r'{self.workspace_dir}')

# Show existing files at start
existing_files = [f for f in os.listdir('.') if not f.endswith('.py')]
if existing_files:
    print(f"Existing files in workspace: {{existing_files}}")

# Track files before execution
_initial_files = set(os.listdir('.'))

# Original code
{code}

# Save any matplotlib figures
if plt.get_fignums():
    for i, fig_num in enumerate(plt.get_fignums()):
        fig = plt.figure(fig_num)
        filename = f'figure_{{i+1}}.png'
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved figure: {{filename}}")

# Post-process CSV files to ensure they have proper headers
import glob
for csv_file in glob.glob('*.csv'):
    try:
        import pandas as pd
        # Try to read the CSV
        df = pd.read_csv(csv_file, header=None)
        # If it has no headers and looks like numeric data, add generic headers
        if len(df.columns) > 1 and df.dtypes.apply(lambda x: x.name in ['float64', 'int64']).all():
            # Add column headers for better display
            df.columns = [f'col_{{i}}' for i in range(len(df.columns))]
            # Save back with headers
            df.to_csv(csv_file, index=False)
            print(f"Added headers to {{csv_file}}")
    except Exception as e:
        # If pandas processing fails, leave the CSV as is
        pass

# Track new files created
_final_files = set(os.listdir('.'))
_new_files = _final_files - _initial_files
if _new_files:
    print(f"Generated files: {{list(_new_files)}}")
"""
        
        temp_file.write(enhanced_code)
        temp_file.close()
        
        try:
            # Execute the code in the persistent workspace
            result = subprocess.run(
                [sys.executable, temp_file.name],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
                timeout=30  # 30 second timeout
            )
            
            # Find newly generated files
            final_files = set(os.listdir(self.workspace_dir))
            new_files = final_files - initial_files - {os.path.basename(temp_file.name)}
            
            generated_files = []
            for file in new_files:
                file_path = os.path.join(self.workspace_dir, file)
                if os.path.isfile(file_path):
                    generated_files.append(file_path)
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'generated_files': generated_files,
                'success': result.returncode == 0,
                'workspace_dir': self.workspace_dir
            }
            
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Code execution timed out after 30 seconds',
                'return_code': -1,
                'generated_files': [],
                'success': False,
                'workspace_dir': self.workspace_dir
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'return_code': -1,
                'generated_files': [],
                'success': False,
                'workspace_dir': self.workspace_dir
            }
        finally:
            # Clean up temp Python file but keep generated files
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def cleanup(self):
        """Clean up - but now this just removes temp files, not the workspace"""
        # Don't remove the workspace directory - let files persist
        pass


def simple_calculator(operation: str, a: float, b: float) -> str:
    """Simple calculator for testing function calls"""
    try:
        a, b = float(a), float(b)
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b if b != 0 else "Error: Division by zero"
        else:
            result = "Error: Unknown operation"
        return json.dumps({"operation": operation, "operands": [a, b], "result": result})
    except ValueError:
        return json.dumps({"error": "Invalid numbers provided"})

def _resolve_ws():
    ws = cl.user_session.get("python_workspace_dir")
    if not ws:
        session_id = cl.user_session.get("id") or "default"
        ws = os.path.join(os.getcwd(), ".files", session_id, "pyws")
    os.makedirs(ws, exist_ok=True)
    return ws
def list_workspace_files() -> str:
    """
    List all files currently in the Python workspace
    
    Returns:
        JSON string with list of files and their info
    """
    try:
        workspace_dir = _resolve_ws()
        
        if not os.path.exists(workspace_dir):
            return json.dumps({
                'success': True,
                'files': [],
                'message': 'Workspace directory does not exist yet'
            })
        
        files_info = []
        for filename in os.listdir(workspace_dir):
            file_path = os.path.join(workspace_dir, filename)
            if os.path.isfile(file_path) and not filename.endswith('.py'):  # Exclude temp Python files
                file_stat = os.stat(file_path)
                file_info = {
                    'filename': filename,
                    'size': file_stat.st_size,
                    'extension': pathlib.Path(filename).suffix.lower(),
                    'modified_time': file_stat.st_mtime
                }
                files_info.append(file_info)
        
        return json.dumps({
            'success': True,
            'files': files_info,
            'count': len(files_info),
            'message': f'Found {len(files_info)} files in workspace'
        })
        
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e),
            'message': f'Failed to list workspace files: {str(e)}'
        })


def upload_file_to_workspace(filename: str, content: bytes) -> str:
    """
    Upload a file to the persistent workspace
    
    Args:
        filename: Name of the file to save
        content: File content as bytes
        
    Returns:
        JSON string with upload result
    """
    try:
        # Create workspace if it doesn't exist
        workspace_dir = _resolve_ws()
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save file to workspace
        file_path = os.path.join(workspace_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Get file info
        file_size = len(content)
        file_ext = pathlib.Path(filename).suffix.lower()
        
        result = {
            'success': True,
            'filename': filename,
            'file_path': file_path,
            'file_size': file_size,
            'file_extension': file_ext,
            'message': f'File "{filename}" uploaded successfully to workspace'
        }
        
        return json.dumps(result)
        
    except Exception as e:
        result = {
            'success': False,
            'filename': filename,
            'error': str(e),
            'message': f'Failed to upload file "{filename}": {str(e)}'
        }
        return json.dumps(result)


def execute_python_code(code: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Execute Python code locally and return formatted results
    
    Args:
        code: Python code to execute
        
    Returns:
        Tuple of (conversation_result_json, files_for_display)
    """
    executor = LocalPythonExecutor()
    
    try:
        result = executor.execute_code(code)
        
        # Process files BEFORE cleanup
        processed_files = []
        for file_path in result['generated_files']:
            try:
                file_info = process_generated_file(file_path)
                if file_info:
                    processed_files.append(file_info)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        # Create a minimal response for the conversation history (no file content)
        conversation_response = {
            'success': result['success'],
            'stdout': result['stdout'][:500] + "..." if len(result['stdout']) > 500 else result['stdout'],
            'stderr': result['stderr'][:500] + "..." if len(result['stderr']) > 500 else result['stderr'],
            'return_code': result['return_code'],
            'files_generated': len(processed_files)
        }
        
        return json.dumps(conversation_response), processed_files
        
    finally:
        executor.cleanup()


def process_generated_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Process a generated file and prepare it for attachment
    
    Args:
        file_path: Path to the generated file
        
    Returns:
        Dict with file information or None if processing failed
    """
    try:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Determine file type
        suffix = pathlib.Path(filename).suffix.lower()
        
        # Read file content
        if suffix in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            # Image file - encode as base64
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            return {
                'filename': filename,
                'type': 'image',
                'size': file_size,
                'content': content,
                'mime_type': f'image/{suffix[1:]}'
            }
        elif suffix == '.csv':
            # CSV file - read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'filename': filename,
                'type': 'csv',
                'size': file_size,
                'content': content,
                'mime_type': 'text/csv'
            }
        else:
            # Text file - read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {
                'filename': filename,
                'type': 'text',
                'size': file_size,
                'content': content,
                'mime_type': 'text/plain'
            }
            
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


def build_tools(vector_store_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Build the tools list for OpenAI API
    
    Args:
        vector_store_id: Optional vector store ID for file search
        
    Returns:
        List of tool definitions
    """
    tools: List[Dict[str, Any]] = [
        {"type": "web_search_preview"},
        {"type": "image_generation"},
        {
            "type": "function",
            "name": "simple_calculator",
            "description": "Perform basic math operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["operation", "a", "b"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "execute_python_code",
            "description": "Execute Python code locally and return results with any generated files. Has access to a persistent workspace where files are saved between executions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Can use matplotlib, pandas, numpy, and other common libraries. Files saved here persist between executions."
                    }
                },
                "required": ["code"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "list_workspace_files",
            "description": "List all files currently available in the Python workspace directory",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "upload_file_to_workspace",
            "description": "Upload a file to the persistent Python workspace so it can be accessed by Python code",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name for the file to be saved in the workspace"
                    },
                    "content": {
                        "type": "string",
                        "description": "Base64 encoded file content"
                    }
                },
                "required": ["filename", "content"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    ]
    
    if vector_store_id:
        tools.append({"type": "file_search", "vector_store_ids": [vector_store_id]})
    
    return tools


@cl.step(type="tool")
async def call_function_tool(call: Dict[str, Any], full_history: List[Dict[str, Any]]) -> str:
    """
    Handle function tool calls
    
    Args:
        call: Function call information
        full_history: Conversation history to update
        
    Returns:
        Function call result
    """
    s = cl.context.current_step
    s.name = f"{call['name']}"

    try:
        args = json.loads(call.get("arguments") or "{}")
    except json.JSONDecodeError:
        args = {}
        out = json.dumps({"error": "Invalid function arguments"})
        full_history.append({
            "role": "function", 
            "name": call["name"], 
            "content": out, 
            "tool_call_id": call["call_id"]
        })
        
        tool_results = cl.user_session.get("tool_results", {})
        tool_results[call["call_id"]] = out
        cl.user_session.set("tool_results", tool_results)
        
        s.input = {"function": call["name"], "arguments": "invalid_json"}
        s.output = out
        s.language = "json"
        return out

    # Execute the appropriate function
    if call["name"] == "simple_calculator":
        out = simple_calculator(args.get("operation"), args.get("a"), args.get("b"))
        
    elif call["name"] == "execute_python_code":
        code = args.get("code", "")
        
        # Execute the code and get both conversation result and files
        conversation_result, processed_files = execute_python_code(code)
        out = conversation_result
        
        # Display execution results and files
        try:
            result_data = json.loads(conversation_result)
            await display_execution_results_simple(result_data, processed_files)
        except Exception as e:
            print(f"Error displaying execution results: {e}")
            
    elif call["name"] == "list_workspace_files":
        out = list_workspace_files()
        
        # Display file list
        try:
            result_data = json.loads(out)
            if result_data['success'] and result_data['files']:
                file_list = []
                for file_info in result_data['files']:
                    size_mb = file_info['size'] / (1024 * 1024)
                    if size_mb >= 1:
                        size_str = f"{size_mb:.1f} MB"
                    else:
                        size_kb = file_info['size'] / 1024
                        if size_kb >= 1:
                            size_str = f"{size_kb:.1f} KB"
                        else:
                            size_str = f"{file_info['size']} bytes"
                    
                    file_list.append(f"- **{file_info['filename']}** ({size_str})")
                
                await cl.Message(
                    content=f"**Workspace Files ({result_data['count']} files):**\n\n" + "\n".join(file_list),
                    author="File Manager"
                ).send()
            else:
                await cl.Message(
                    content="**Workspace is empty** - no files found",
                    author="File Manager"  
                ).send()
        except Exception as e:
            print(f"Error displaying file list: {e}")
            
    elif call["name"] == "upload_file_to_workspace":
        filename = args.get("filename", "")
        content_b64 = args.get("content", "")
        
        try:
            # Decode base64 content
            content_bytes = base64.b64decode(content_b64)
            out = upload_file_to_workspace(filename, content_bytes)
            
            # Display upload confirmation
            result_data = json.loads(out)
            if result_data['success']:
                await cl.Message(
                    content=f"**File uploaded successfully!**\n\n"
                           f"**{result_data['filename']}** has been saved to the Python workspace.\n"
                           f"Size: {result_data['file_size']:,} bytes\n"
                           f"You can now analyze this file using Python code.",
                    author="File Manager"
                ).send()
            else:
                await cl.Message(
                    content=f"**Upload failed:** {result_data['message']}",
                    author="File Manager"
                ).send()
        except Exception as e:
            out = json.dumps({"success": False, "error": f"Failed to process upload: {str(e)}"})
            await cl.Message(
                content=f"**Upload failed:** Error processing file upload",
                author="File Manager"
            ).send()
            
    else:
        out = json.dumps({"error": f"Unknown function {call['name']}"})

    # Update tool results and history
    tool_results = cl.user_session.get("tool_results", {})
    tool_results[call["call_id"]] = out
    cl.user_session.set("tool_results", tool_results)

    full_history.append({
        "role": "function", 
        "name": call["name"], 
        "content": out, 
        "tool_call_id": call["call_id"]
    })

    s.input = {"function": call["name"], "arguments": args}
    s.output = out
    s.language = "json"
    return out


async def display_execution_results_simple(result_data: Dict[str, Any], processed_files: List[Dict[str, Any]]):
    """
    Display Python execution results with minimal overhead
    
    Args:
        result_data: Execution result data
        processed_files: List of processed file information
    """
    # Display stdout if present
    if result_data.get('stdout'):
        await cl.Message(
            content=f"**Output:**\n```\n{result_data['stdout']}\n```",
            author="Python Executor"
        ).send()
    
    # Display stderr if present
    if result_data.get('stderr'):
        await cl.Message(
            content=f"**Error:**\n```\n{result_data['stderr']}\n```",
            author="Python Executor"
        ).send()
    
    # Display processed files
    for file_info in processed_files:
        try:
            await display_generated_file(file_info)
        except Exception as e:
            print(f"Error displaying file: {e}")


async def display_generated_file(file_info: Dict[str, Any]):
    """
    Display a generated file with appropriate preview
    
    Args:
        file_info: File information dictionary
    """
    filename = file_info['filename']
    file_type = file_info['type']
    content = file_info['content']
    
    # Create temporary file for Chainlit
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=pathlib.Path(filename).suffix)
    
    try:
        if file_type == 'image':
            # Decode base64 image
            image_data = base64.b64decode(content)
            temp_file.write(image_data)
            temp_file.flush()
            
            await cl.Message(
                content=f"**{filename}** — Generated image",
                author="Python Executor",
                elements=[
                    cl.Image(path=temp_file.name, name=filename, display="inline"),
                    cl.File(name=filename, path=temp_file.name)
                ]
            ).send()
            
        elif file_type == 'csv':
            # Write CSV content
            temp_file.write(content.encode('utf-8'))
            temp_file.flush()
            
            # Use Chainlit's Dataframe component
            try:
                import pandas as pd
                import io
                df = pd.read_csv(io.StringIO(content))
                
                await cl.Message(
                    content=f"**{filename}** — Generated CSV file with {len(df)} rows and {len(df.columns)} columns",
                    author="Python Executor",
                    elements=[
                        cl.Dataframe(data=df, name=filename, display="inline"),
                        cl.File(name=filename, path=temp_file.name)
                    ]
                ).send()
                
            except Exception as e:
                # Fallback to text preview if dataframe fails
                print(f"Dataframe display error: {e}")
                lines = content.split('\n')[:11]  # First 10 lines + header
                preview_md = "```csv\n" + "\n".join(lines) + "\n```"
                
                await cl.Message(
                    content=f"**{filename}** — Generated CSV file. Preview:\n\n{preview_md}",
                    author="Python Executor",
                    elements=[cl.File(name=filename, path=temp_file.name)]
                ).send()
            
        else:
            # Text file
            temp_file.write(content.encode('utf-8'))
            temp_file.flush()
            
            # Show preview of text content (first 1000 chars)
            preview = content[:1000] + ("..." if len(content) > 1000 else "")
            
            await cl.Message(
                content=f"**{filename}** — Generated text file. Preview:\n\n```\n{preview}\n```",
                author="Python Executor", 
                elements=[cl.File(name=filename, path=temp_file.name)]
            ).send()
            
    finally:
        temp_file.close()


@cl.step(type="tool")
async def show_tool_progress(tool_type: str, status: str):
    """Display tool execution progress"""
    s = cl.context.current_step
    status_messages = {
        "web_search_call.in_progress": "Starting web search...",
        "web_search_call.searching": "Searching the web...",
        "web_search_call.completed": "Web search completed",
        "python_execution.in_progress": "Starting Python code execution...",
        "python_execution.running": "Running Python code...",
        "python_execution.completed": "Python code execution completed",
        "image_generation_call.in_progress": "Starting image generation...",
        "image_generation_call.generating": "Generating image...",
        "image_generation_call.completed": "Image generation completed",
    }
    s.name = "Tool Progress"
    s.input = tool_type
    s.output = status_messages.get(f"{tool_type}.{status}", f"{tool_type}: {status}")


@cl.step(type="tool")
async def show_reasoning_summary(summary_text: str):
    """Display model reasoning summary"""
    s = cl.context.current_step
    s.name = "Reasoning Summary"
    s.input = "Model's reasoning process"
    s.output = summary_text
    s.language = "markdown"


@cl.step(type="tool")
async def show_python_code(code: str):
    """Display the Python code that will be executed"""
    s = cl.context.current_step
    s.name = "Python Code to Execute"
    s.input = "Code submitted for execution"
    s.output = code
    s.language = "python"