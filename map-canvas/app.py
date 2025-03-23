import json
import chainlit as cl
from anthropic import AsyncAnthropic

SYSTEM = "you are a helpful assistant."
MODEL_NAME = "claude-3-5-sonnet-latest"
c = AsyncAnthropic()


@cl.step(type="tool")
async def move_map_to(latitude: float, longitude: float):
    await open_map()

    fn = cl.CopilotFunction(
        name="move-map", args={"latitude": latitude, "longitude": longitude}
    )
    await fn.acall()

    return "Map moved!"


tools = [
    {
        "name": "move_map_to",
        "description": "Move the map to the given latitude and longitude.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "string",
                    "description": "The latitude of the location to move the map to",
                },
                "longitude": {
                    "type": "string",
                    "description": "The longitude of the location to move the map to",
                },
            },
            "required": ["latitude", "longitude"],
        },
    }
]

TOOL_FUNCTIONS = {
    "move_map_to": move_map_to,
}


async def call_claude(chat_messages):
    msg = cl.Message(content="", author="Claude")

    async with c.messages.stream(
        max_tokens=1024,
        system=SYSTEM,
        messages=chat_messages,
        tools=tools,
        model=MODEL_NAME,
    ) as stream:
        async for text in stream.text_stream:
            await msg.stream_token(text)

    await msg.send()
    response = await stream.get_final_message()

    return response


async def call_tool(tool_use):
    tool_name = tool_use.name
    tool_input = tool_use.input

    tool_function = TOOL_FUNCTIONS.get(tool_name)

    if tool_function:
        try:
            return await tool_function(**tool_input)
        except TypeError:
            return json.dumps({"error": f"Invalid input for {tool_name}"})
    else:
        return json.dumps({"error": f"Invalid tool: {tool_name}"})


async def open_map():
    map_props = {"latitude": 37.7749, "longitude": -122.4194, "zoom": 12}
    custom_element = cl.CustomElement(name="Map", props=map_props, display="inline")
    await cl.ElementSidebar.set_title("canvas")
    await cl.ElementSidebar.set_elements([custom_element], key="map-canvas")


@cl.action_callback("close_map")
async def on_test_action():
    await cl.ElementSidebar.set_elements([])


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Paris",
            message="Show me Paris.",
        ),
        cl.Starter(
            label="NYC",
            message="Show me NYC.",
        ),
        cl.Starter(
            label="Tokyo",
            message="Show me Tokyo.",
        ),
    ]


@cl.on_chat_start
async def on_start():
    cl.user_session.set("chat_messages", [])

    await open_map()


@cl.on_message
async def on_message(msg: cl.Message):
    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "user", "content": msg.content})
    response = await call_claude(chat_messages)

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == "tool_use")
        tool_result = await call_tool(tool_use)

        messages = [
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(tool_result),
                    }
                ],
            },
        ]

        chat_messages.extend(messages)
        response = await call_claude(chat_messages)

    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )

    chat_messages = cl.user_session.get("chat_messages")
    chat_messages.append({"role": "assistant", "content": final_response})
