from openai import AsyncClient
import json
import ast
import os
import chainlit as cl
from functions.FunctionManager import FunctionManager
import inspect
import os
import tiktoken
import importlib
import json


openai_client = AsyncClient(api_key=os.environ.get("OPENAI_API_KEY"))


# 获取plugins目录下所有的子目录，忽略名为'__pycache__'的目录
plugin_dirs = [
    d
    for d in os.listdir("plugins")
    if os.path.isdir(os.path.join("plugins", d)) and d != "__pycache__"
]

functions = []

# 遍历每个子目录（即每个插件）
for dir in plugin_dirs:
    # 尝试读取插件的配置文件
    try:
        with open(f"plugins/{dir}/config.json", "r") as f:
            config = json.load(f)
        enabled = config.get("enabled", True)
    except FileNotFoundError:
        # 如果配置文件不存在，我们默认这个插件应该被导入
        enabled = True

    # 检查这个插件是否应该被导入
    if not enabled:
        continue

    # 动态导入每个插件的functions模块
    module = importlib.import_module(f"plugins.{dir}.functions")

    # 获取模块中的所有函数并添加到functions列表中
    functions.extend(
        [obj for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]
    )

function_manager = FunctionManager(functions=functions)
print("functions:", function_manager.generate_functions_array())

max_tokens = 5000


def __truncate_conversation(conversation) -> None:
    """
    Truncate the conversation
    """
    # 第一条取出来
    system_con = conversation[0]
    # 去掉第一条
    conversation = conversation[1:]
    while True:
        if get_token_count(conversation) > max_tokens and len(conversation) > 1:
            # Don't remove the first message
            conversation.pop(1)
        else:
            break
    # 再把第一条加回来
    conversation.insert(0, system_con)
    return conversation


# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def get_token_count(conversation) -> int:
    """
    Get token count
    """
    encoding = tiktoken.encoding_for_model("gpt-4")

    num_tokens = 0
    for message in conversation:
        # every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


MAX_ITER = 100


async def on_message(message: cl.Message):
    user_message = message.content
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": user_message})

    cur_iter = 0

    while cur_iter < MAX_ITER:
        # OpenAI call
        openai_message = {"role": "", "content": ""}
        function_ui_message = None
        content_ui_message = cl.Message(content="")
        stream_resp = None
        send_message = __truncate_conversation(message_history)
        try:
            stream = openai_client.chat.completions.create(
                model="gpt-4",
                messages=send_message,
                stream=True,
                function_call="auto",
                functions=function_manager.generate_functions_array(),
                temperature=0,
            )
            async for part in stream:
                new_delta = part.choices[0].delta
                (
                    openai_message,
                    content_ui_message,
                    function_ui_message,
                ) = await process_new_delta(
                    new_delta, openai_message, content_ui_message, function_ui_message
                )
        except Exception as e:
            print(e)
            cur_iter += 1
            continue

        if stream_resp is None:
            break

        message_history.append(openai_message)
        if function_ui_message is not None:
            await function_ui_message.send()

        if stream_resp.choices[0]["finish_reason"] == "stop":
            break
        elif stream_resp.choices[0]["finish_reason"] != "function_call":
            raise ValueError(stream_resp.choices[0]["finish_reason"])
        # if code arrives here, it means there is a function call
        function_name = openai_message.get("function_call").get("name")
        print(openai_message.get("function_call"))
        try:
            arguments = json.loads(openai_message.get("function_call").get("arguments"))
        except:
            arguments = ast.literal_eval(
                openai_message.get("function_call").get("arguments")
            )

        function_response = await function_manager.call_function(
            function_name, arguments
        )
        # print(function_response)

        message_history.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )

        await cl.Message(
            author=function_name,
            content=str(function_response),
            language="json",
            parent_id=content_ui_message.id,
        ).send()
        cur_iter += 1


async def process_new_delta(
    new_delta, openai_message, content_ui_message, function_ui_message
):
    if new_delta.role:
        openai_message["role"] = new_delta.role

    new_content = new_delta.content or ""
    openai_message["content"] += new_content
    await content_ui_message.stream_token(new_content)
    if new_delta.function_call:
        if new_delta.function_call.name:
            openai_message["function_call"] = {"name": new_delta.function_call.name}
            await content_ui_message.send()
            function_ui_message = cl.Message(
                author=new_delta.function_call.name,
                content="",
                parent_id=content_ui_message.id,
                language="json",
            )
            await function_ui_message.stream_token(new_delta.function_call.name)

        if new_delta.function_call.arguments:
            if "arguments" not in openai_message["function_call"]:
                openai_message["function_call"]["arguments"] = ""
            openai_message["function_call"][
                "arguments"
            ] += new_delta.function_call.arguments
            await function_ui_message.stream_token(new_delta.function_call.arguments)
    return openai_message, content_ui_message, function_ui_message


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": """
                you are now chatting with an AI assistant. The assistant is helpful, creative, clever, and very friendly.
            """,
            }
        ],
    )


@cl.on_message
async def run_conversation(message: cl.Message):
    await on_message(message)
