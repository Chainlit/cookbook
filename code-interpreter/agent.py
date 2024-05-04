import json, base64

import ast
import os, asyncio
from openai import AsyncOpenAI
from e2b_code_interpreter import CodeInterpreter
import chainlit as cl

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

MAX_ITER = 5

# MODEL_NAME = "llama3-70b-8192"

SYSTEM_PROMPT = """you are a python data scientist. you are given tasks to complete and you run python code to solve them.
- the python code runs in jupyter notebook.
- every time you call `execute_python` tool, the python code is executed in a separate cell. it's okay to multiple calls to `execute_python`.
- display visualizations using matplotlib or any other visualization library directly in the notebook. don't worry about saving the visualizations to a file.
- you have access to the internet and can make api requests.
- you also have access to the filesystem and can read/write files.
- you can install any pip package (if it exists) if you need to but the usual packages for data analysis are already preinstalled.
- you can run any python code you want, everything is running in a secure sandbox environment"""


TOOLS = [
  {
    "type": "function",
      "function": {
        "name": "execute_python",
        "description": "Execute python code in a Jupyter notebook cell and returns any result, stdout, stderr, display_data, and error.",
        "parameters": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "The python code to execute in a single cell.",
            }
          },
          "required": ["code"],
        },
      },
  }
]

class DataAgent:

    def __init__(self, sandbox=None) -> None:
        
        self.settings = {
            "model": "gpt-4",
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0,
        }
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        if not sandbox:
            sandbox = CodeInterpreter()
        self.sandbox = sandbox

    async def close(self):
        self.sandbox.close()

    async def save_files(self, files):
        for file in files:
            file_path = file.path
            with open(file_path, "rb") as f:
                remote_path = self.sandbox.upload_file(f)


    async def execute_python(self, code):
        print("Running code interpreter...")
        exec = await asyncio.to_thread(
            self.sandbox.notebook.exec_cell,
            code,
            on_stderr=lambda stderr: print("[Code Interpreter]", stderr),
            on_stdout=lambda stdout: print("[Code Interpreter]", stdout),
            # You can also stream code execution results
            # on_result=...
        )
        result = exec.results[0]
        for format, data in result.raw.items():
            if format == "image/png":
                with open("image.png", "wb") as f:
                    f.write(base64.b64decode(data))
    
        if exec.error:
            print("[Code Interpreter ERROR]", exec.error)
        else:
            print("\n HELLOOOOOO \n", exec.results[0].__dict__)
            return exec.results[0].__dict__["text"]

    async def run(self, messages) -> cl.Step:
        # TODO: add system message.
        cur_iter = 0
        while cur_iter < MAX_ITER:
            
            response = await client.chat.completions.create(
                messages=messages, **self.settings
            )
            print("\n\n",response, "\n\n")
            messages.append(response.choices[0].message)
            tool_calls = response.choices[0].message.tool_calls

            if tool_calls:
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors

                async def call_function(tool_call):
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    function_to_call = getattr(self, function_name)
                    print(function_to_call, function_args)
                    function_response = await function_to_call(**function_args)
                    return {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }

                # Use asyncio.gather to make function calls in parallel
                print(tool_calls)
                function_responses = await asyncio.gather(
                    *(call_function(tool_call) for tool_call in tool_calls)
                )

                # Extend conversation with all function responses
                messages.extend(function_responses)
            else:
                break

            cur_iter += 1

        return messages






# dataagent = DataAgent()

# messages = [{"role":"user", "content":"plot a sin wave"}]
# asyncio.run(dataagent.run(messages))

# asyncio.run(dataagent.close())