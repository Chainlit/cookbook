import chainlit as cl
import chainlit.cli
import os, sys
import shutil
import json
from typing import Any, Optional, Union
from click.testing import CliRunner
import uuid

import appbuilder
from appbuilder.core.message import Message
from appbuilder.utils.logger_util import logger
from appbuilder.core.context import init_context
from appbuilder.core.user_session import UserSession
from appbuilder.core.console.appbuilder_client.data_class import ToolChoice, Action


class ChainlitRuntime(object):
    """ChainlitRuntime 是对组件和应用调用的chainlit服务化封装。
    """
    def __init__(self,
            component,
            user_session_config: Optional[Union[Any, str]] = None,
            user_session: Optional[UserSession] = None,
            tool_choice: ToolChoice = None 
        ):
        """init

        Args:
            component (Component): 需要服务化的组件实例
            user_session_config (sqlalchemy.engine.URL|str|None): Session 输出存储配置字符串。默认使用 sqlite:///user_session.db
                遵循 sqlalchemy 后端定义，参考文档：https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls
            user_session (UserSession): 用户会话管理器，如果不指定则自动生成一个默认的 UserSession
            tool_choice (ToolChoice): 可用于Agent强制执行的组件工具

        """
        self.component = component
        if user_session is None:
            if user_session_config is None:
                self.user_session = UserSession()
                logger.info("init user_session with default UserSession")
            else:
                self.user_session = UserSession(user_session_config)
                logger.info("init user_session with user_session_config")
        else:
            self.user_session = user_session
        self.tool_choice = tool_choice
        self._prepare_chainlit_readme()
    
    def chat(self, message: Message, stream: bool = False, **kwargs) -> Message:
        """
        执行一次对话

        Args:
            message (Message): 该次对话用户输入的 Message
            stream (bool): 是否流式请求
            **args: 其他参数，会被透传到 component

        Returns:
            Message(Message): 返回的 Message
        """
        return self.component.run(message=message, stream=stream, **kwargs)

    def _prepare_chainlit_readme(self):
        """
        准备 Chainlit 的 README 文件
        从 utils 文件夹中拷贝 chainlit.md 文件到当前工作目录下，如果当前工作目录下已存在 chainlit.md 文件，则不拷贝。
        
        Args:
            None
        
        Returns:
            None
        
        Raises:
            None 
        """
        try:
            # 获取当前python命令执行的路径，而不是文件的位置
            cwd_path = os.getcwd()
            # 获取当前文件的路径所在文件夹
            current_file_path = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            logger.info("current_file_path")
            chainlit_readme_path = os.path.join(
                current_file_path, "chainlit.md")
            if not os.path.exists(chainlit_readme_path):
                raise FileNotFoundError(f"Chainlit readme file not found at {chainlit_readme_path}")
            
            # 拷贝chainlit_readme到cwd_path
            # 如果cwd_path下已经存在chainlit_readme，则不拷贝
            if not os.path.exists(os.path.join(cwd_path, "chainlit.md")):
                shutil.copy(chainlit_readme_path, cwd_path)
                logger.info("chainlit readme file copied successfully")
        except:
            logger.error("Failed to copy chainlit.md to current directory")   

    def chainlit_component(self, host='0.0.0.0', port=8091):
        """
        将 component 服务化，提供 chainlit demo 页面

        Args:
            host (str): 服务 host
            port (int): 服务 port

        Returns:
            None
        """
        @cl.on_message  # this function will be called every time a user inputs a message in the UI
        async def main(message: cl.Message):
            session_id = cl.user_session.get("id")
            request_id = str(uuid.uuid4())
            init_context(session_id=session_id, request_id=request_id)
            msg = cl.Message(content="")
            await msg.send()
            stream_message = self.chat(Message(message.content), stream=True)

            for part in stream_message.content:
                if token := part or "":
                    await msg.stream_token(token)
            await msg.update()
            self.user_session._post_append()

        if os.getenv('APPBUILDER_RUN_CHAINLIT') == '1':
            pass
        else:
            os.environ['APPBUILDER_RUN_CHAINLIT'] = '1'
            target = sys.argv[0]
            runner = CliRunner()
            runner.invoke(
                chainlit.cli.chainlit_run, [target, '--watch', "--port", port, "--host", host])
        

    def chainlit_agent(self, host='0.0.0.0', port=8091):
        """
        将 appbuilder client 服务化，提供 chainlit demo 页面

        Args:
            host (str): 服务 host
            port (int): 服务 port

        Returns:
            None
        """

        conversation_ids = []
        interrupt_dict = {}

        def _chat(message: cl.Message):
            if len(conversation_ids) == 0:
                raise ValueError("create new conversation failed!")
            conversation_id = conversation_ids[-1]
            file_ids = []
            if len(message.elements) > 0:
                file_id = self.component.upload_local_file(
                    conversation_id, message.elements[0].path)
                file_ids.append(file_id)

            interrupt_ids = interrupt_dict.get(conversation_id, [])
            interrupt_event_id = interrupt_ids.pop() if len(interrupt_ids) > 0 else None
            action = None
            if interrupt_event_id is not None:
                action = Action.create_resume_action(interrupt_event_id)
            
            tmp_message = self.component.run(conversation_id=conversation_id, query=message.content, file_ids=file_ids,
                                      stream=True, tool_choice=self.tool_choice, action=action)
            res_message=list(tmp_message.content)
            
            interrupt_event_id = None
            for ans in res_message:
                for event in ans.events:
                    if event.content_type == "chatflow_interrupt":
                        interrupt_event_id = event.detail.get("interrupt_event_id")
                    if event.content_type == "publish_message" and event.event_type == "chatflow":
                        answer = event.detail.get("message")
                        ans.answer += answer
                        
            if interrupt_event_id is not None:
                interrupt_ids.append(interrupt_event_id)
                interrupt_dict[conversation_id] = interrupt_ids
            tmp_message.content = res_message
            return tmp_message

        @cl.on_chat_start
        async def start():
            session_id = cl.user_session.get("id")
            request_id = str(uuid.uuid4())
            init_context(session_id=session_id, request_id=request_id)
            conversation_ids.append(self.component.create_conversation())
            interrupt_dict[conversation_ids[-1]] = []

        @cl.on_message  # this function will be called every time a user inputs a message in the UI
        async def main(message: cl.Message):
            msg = cl.Message(content="")
            await msg.send()
            await msg.update()

            stream_message = _chat(message)
            detail_json_list = []
            for part in stream_message.content:
                if token := part.answer or "":
                    await msg.stream_token(token)
                for event in part.events:
                    detail = event.detail
                    detail_json = json.dumps(
                        detail, indent=4, ensure_ascii=False)
                    detail_json_list.append(detail_json)
            await msg.update()

            @cl.step(name="详细信息")
            def show_json(detail_json):
                return "```json\n" + detail_json + "\n```"
            for detail_json in detail_json_list:
                if len(detail_json) > 2:
                    show_json(detail_json)
            await msg.update()
            self.user_session._post_append()

        if os.getenv('APPBUILDER_RUN_CHAINLIT') == '1':
            pass
        else:
            os.environ['APPBUILDER_RUN_CHAINLIT'] = '1'
            target = sys.argv[0]
            runner = CliRunner()
            runner.invoke(
                chainlit.cli.chainlit_run, [target, '--watch', "--port", port, "--host", host])

