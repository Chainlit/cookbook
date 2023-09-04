from typing import Union

from fastapi.responses import StreamingResponse

from chainlit.playground.provider import BaseProvider
from chainlit.prompt import PromptMessage
from chainlit.sync import make_async
from chainlit import input_widget
from typing import List
from copy import deepcopy as dc

class LangChainModelKwargsGenericProvider(BaseProvider):
    from langchain.chat_models.base import BaseChatModel
    from langchain.llms.base import LLM

    llm: Union[LLM, BaseChatModel]

    def __init__(
        self,
        id: str,
        name: str,
        inputs: List[input_widget.InputWidget],
        llm: Union[LLM, BaseChatModel],
        is_chat: bool = False,
    ):
        super().__init__(
            id=id,
            name=name,
            env_vars={},
            inputs=inputs,
            is_chat=is_chat,
        )
        self.llm = dc(llm)
        self.llm_model_kwargs = dc(llm.model_kwargs)

    def prompt_message_to_langchain_message(self, message: PromptMessage):
        from langchain.schema.messages import (
            AIMessage,
            FunctionMessage,
            HumanMessage,
            SystemMessage,
        )

        content = "" if message.formatted is None else message.formatted
        if message.role == "user":
            return HumanMessage(content=content)
        elif message.role == "assistant":
            return AIMessage(content=content)
        elif message.role == "system":
            return SystemMessage(content=content)
        elif message.role == "function":
            return FunctionMessage(
                content=content, name=message.name if message.name else "function"
            )
        else:
            raise ValueError(f"Got unknown type {message}")

    def format_message(self, message, prompt):
        message = super().format_message(message, prompt)
        return self.prompt_message_to_langchain_message(message)

    def message_to_string(self, message: PromptMessage) -> str:
        return message.to_string()

    async def create_completion(self, request):
        from langchain.schema.messages import BaseMessageChunk
        
        # deepcopy the dict
        copy_model_kwargs = dc(self.llm_model_kwargs)

        # filter in the model kwargs from all the args
        new_model_kwargs = {k: v for k, v in request.prompt.settings.items() if k in copy_model_kwargs.keys()}

        # update to the new model_kwargs
        copy_model_kwargs.update(new_model_kwargs)

        await super().create_completion(request)

        messages = self.create_prompt(request)

        self.llm.model_kwargs.update(copy_model_kwargs)

        # root level params 
        # Useful if you have params at the llm class level
        # root_kwargs = {k: v for k, v in request.prompt.settings.items() if k not in copy_model_kwargs.keys()}

        # print("root", root_kwargs)
        # for k, v in root_kwargs.items():
        #     setattr(self.llm, k, v) 


        stream = make_async(self.llm.stream)

        result = await stream(
            input=messages,
        )

        def create_event_stream():
            try:
                for chunk in result:
                    if isinstance(chunk, BaseMessageChunk):
                        yield chunk.content
                    else:
                        yield chunk
            except Exception as e:
                # The better solution would be to return a 500 error, but
                # langchain raises the error in the stream, and the http
                # headers have already been sent.
                yield f"Failed to create completion: {str(e)}"

        return StreamingResponse(create_event_stream())
