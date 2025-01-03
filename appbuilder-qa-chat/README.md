## What is AppBuilder👋
[Baidu Smart Cloud Qianfan AppBuilder](https://appbuilder.cloud.baidu.com/): an enterprise-level one-stop big model and AI native application development and service platform.


- [AppBuilder official website](https://appbuilder.cloud.baidu.com/)
- [AppBuilder-SDK open source code repository](https://github.com/baidubce/app-builder)
- [AppBuilder Documentation Center](https://cloud.baidu.com/doc/AppBuilder/index.html)

## How to use AppBuilder & Chainlit visualization function💻
The `ChainlitRuntime` module in the current SDK implements basic visualization functions based on Chainlit, and supports AppBuilderClient + capability components to achieve visualization interaction.
- The `chainlit_component` interface supports simple interaction of basic components
- The `chainlit_agent` interface supports advanced interaction of AppBuilderClient, providing the functions of creating new sessions and uploading files

If you have more requirements for visualization, you can refer to the code in the AppBuilder SDK and perform secondary development based on Chainlit.

### 1. Instantiate `ChainlitRuntime() -> ChainlitRuntime`

#### Parameters

| Parameter name | Parameter type | Required | Description | Example value |
|--------|--------|------------|-----------|-------|
| component | Component | Yes | Runnable Component, need to implement run(message, stream, **args) method | Playground(prompt_template="{query}", model="ERNIE-Bot") |
| user_session_config | sqlalchemy.engine.URL, str, None | No | Session output storage configuration string. Defaults to sqlite:///user_session.db | "sqlite:///user_session.db" |
| user_session| UserSession | No | User session manager, if not specified, automatically generates a default UserSession | UserSession(user_session_config) |
| tool_choice| ToolChoice| No | Component tool that can be used for Agent enforcement | |

#### behavior

Returns a debugging Agent service

#### examples

```python
import os
import appbuilder
from appbuilder.utils.chainlit_deploy import ChainlitRuntime
# Before using the component, please go to Qianfan AppBuilder official website to create a key. For details, see：https://console.bce.baidu.com/ai_apaas/secretKey
os.environ["APPBUILDER_TOKEN"] = '...'
component = appbuilder.Playground(
    prompt_template="{query}",
    model="eb-4"
)
agent = ChainlitRuntime(component=component)
```

### 2、Run the Agent service`ChainlitRuntime.chat(message: Message, stream: bool = False, **args) -> Message`

#### Parameters

| Parameter name | Parameter type | Description | Example value |
|--------|--------|------------|-----------|
| message | Message | The message entered by the user in this conversation | "Correct Message" |
| stream | bool | Whether to use streaming request. Default is False | False |

#### behavior

Run an Agent service and perform a conversation

#### examples

```python
import os
import appbuilder
from appbuilder.utils.chainlit_deploy import ChainlitRuntime
# Before using the component, please go to Qianfan AppBuilder official website to create a key. For details, see：https://console.bce.baidu.com/ai_apaas/secretKey
os.environ["APPBUILDER_TOKEN"] = '...'
component = appbuilder.Playground(
    prompt_template="{query}",
    model="eb-4"
)
agent = ChainlitRuntime(component=component)
message = appbuilder.Message({"query": "你好"})
print(agent.chat(message, stream=False))
```

### 3、Provides chainlit component dialogue page`ChainlitRuntime.chainlit_component(host='0.0.0.0', port=8091)`


#### Parameters

| Parameter name | Parameter type | Description | Example value |
|--------|--------|------------|-----------|
| host | string | Service host address, default is '0.0.0.0' | "0.0.0.0" |
| port | int | Service port number, default is 8092 | 8091 |

#### behavior

Make component a service and provide chainlit page

#### examples

##### basic
```python
import os
import appbuilder
from appbuilder.utils.chainlit_deploy import ChainlitRuntime

# Before using the component, please go to Qianfan AppBuilder official website to create a key. For details, see：https://console.bce.baidu.com/ai_apaas/secretKey
os.environ["APPBUILDER_TOKEN"] = '...'

component = appbuilder.Playground(
    prompt_template="{query}",
    model="ERNIE-Bot"
)

agent = ChainlitRuntime(component=component)
agent.chainlit_component(port=8091)
```

##### advanced
Implement your own components and use UserSession to store historical conversation content

```python
import os
import logging
from appbuilder.core.component import Component
from appbuilder import (
    UserSession, Message, QueryRewrite, Playground,
)
from appbuilder.utils.chainlit_deploy import ChainlitRuntime
# Before using the component, please go to Qianfan AppBuilder official website to create a key. For details, see：https://console.bce.baidu.com/ai_apaas/secretKey
os.environ["APPBUILDER_TOKEN"] = 'YOUR_APPBUILDER_TOKEN'
class PlaygroundWithHistory(Component):
    def __init__(self):
        super().__init__()
        self.query_rewrite = QueryRewrite(model="Qianfan-Agent-Speed-8k")
        self.play = Playground(
            prompt_template="{query}",
            model="eb-4"
        )
    def run(self, message: Message, stream: bool=False):
        user_session = UserSession()
        # Get Session History Data
        history_queries = user_session.get_history("query", limit=1)
        history_answers = user_session.get_history("answer", limit=1)
        if history_queries and history_answers:
            history = []
            for query, answer in zip(history_queries, history_answers):
                history.extend([query.content, answer.content])
            logging.info(f"history: {history}")
            message = self.query_rewrite(
                Message(history + [message.content]), rewrite_type="带机器人回复")
        logging.info(f"message: {message}") 
        answer = self.play.run(message, stream)
        # Save this round of data
        user_session.append({
            "query": message,
            "answer": answer,
        }) 
        return answer

agent = ChainlitRuntime(component=PlaygroundWithHistory())
agent.chainlit_component(port=8091)
```

### 4、Make appbuilder client a service and provide chainlit demo page`ChainlitRuntime.chainlit_agent(host='0.0.0.0', port=8091)`
Currently, workflow agent and autonomous planning agent applications are supported.

#### Parameters

| Parameter name | Parameter type | Description | Example value |
|--------|--------|------------|-----------|
| host | string | Service host address, default is '0.0.0.0' | "0.0.0.0" |
| port | int | Service port number, default is 8092 | 8091 |

#### behavior

Make appbuilder client a service and provide chainlit page

#### examples
You can view the published AppBuilder application ID in the [console](https://console.bce.baidu.com/ai_apaas/personalSpace/app).

```python
import appbuilder
from appbuilder.utils.chainlit_deploy import ChainlitRuntime
import os

os.environ["APPBUILDER_TOKEN"] = '...'
app_id = '...'  # The AppBuilder application ID has been published and can be viewed on the console
client = appbuilder.AppBuilderClient(app_id)
agent = ChainlitRuntime(component=client)
agent.chainlit_agent(port=8091)
```

