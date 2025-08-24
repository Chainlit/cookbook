import json, os
from openai import AsyncOpenAI
import chainlit as cl

# ─────────────────── 1. OpenAI & Chainlit ────────────────────────────────────
cl.instrument_openai()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────── 2. demo tools ───────────────────────────────────────────
def get_current_weather(location, unit):
    unit = unit or "fahrenheit"
    return json.dumps(
        {"location": location, "temperature": "60", "unit": unit, "forecast": ["windy"]}
    )


def search_web(query):
    return json.dumps(
        {
            "query": query,
            "results": [
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "snippet": f"Mock for '{query}'.",
                },
                {
                    "title": "Result 2",
                    "url": "https://example.com/2",
                    "snippet": f"Another mock for '{query}'.",
                },
            ],
            "total_results": 2,
        }
    )


tools = [
    {
        "type": "function",
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": ["string", "null"], "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location", "unit"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_web",
        "description": "Search the web",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
MAX_ITER = 20
DEV_PROMPT = (
    "You are a helpful assistant. Use tools when needed. "
    "Talk in Ned Flanders Simpsons style always."
)

# ─────────────────── 3. conversation helpers ────────────────────────────────
@cl.on_chat_start
def _start():
    cl.user_session.set("full_conversation_history", [])
    cl.user_session.set("previous_response_id", None)
    cl.user_session.set("tool_results", {})
    cl.user_session.set("dev_prompt", DEV_PROMPT)


# Enhanced debug view with full conversation history
@cl.step(type="tool")
async def show_full_conversation(current_message, full_history):
    s = cl.context.current_step
    s.name, s.input = "Full Conversation History", current_message

    # Format history for better readability
    formatted_history = []
    for msg in full_history:
        if isinstance(msg, dict):
            role = msg.get("role")
            if role in ("system", "user", "assistant"):
                formatted_history.append({"role": role, "content": msg["content"]})
            elif role == "function" or msg.get("name"):
                formatted_history.append(
                    {
                        "role": "function",
                        "name": msg.get("name", "unknown_function"),
                        "content": msg["content"],
                        "tool_call_id": msg.get("tool_call_id", "unknown_id"),
                    }
                )
            else:
                formatted_history.append(msg)
        else:
            formatted_history.append(msg)

    s.output, s.language = formatted_history, "json"
    return formatted_history


@cl.step(type="tool")
async def call_function_tool(call, full_history):
    # Set step name to actual function name for better visibility
    s = cl.context.current_step
    s.name = f"{call['name']}"

    try:
        args = json.loads(call.get("arguments") or "{}")
    except json.JSONDecodeError:
        args = {}
        out = json.dumps({"error": "Invalid function arguments"})
        full_history.append(
            {
                "role": "function",
                "name": call["name"],
                "content": out,
                "tool_call_id": call["call_id"],
            }
        )
        tool_results = cl.user_session.get("tool_results")
        tool_results[call["call_id"]] = out
        cl.user_session.set("tool_results", tool_results)
        s.input = {"function": call["name"], "arguments": "invalid_json"}
        s.output, s.language = out, "json"
        return out

    if call["name"] == "get_current_weather":
        out = get_current_weather(args.get("location", "Unknown"), args.get("unit"))
    elif call["name"] == "search_web":
        out = search_web(args.get("query", ""))
    else:
        out = json.dumps({"error": f"Unknown function {call['name']}"})

    # Cache successful result
    tool_results = cl.user_session.get("tool_results")
    tool_results[call["call_id"]] = out
    cl.user_session.set("tool_results", tool_results)

    full_history.append(
        {
            "role": "function",
            "name": call["name"],
            "content": out,
            "tool_call_id": call["call_id"],
        }
    )

    s.input = {"function": call["name"], "arguments": args}
    s.output, s.language = out, "json"
    return out


async def _ask_gpt5(input_messages, prev_id=None):
    dev_input = []
    if not prev_id:
        dev_input.append({
            "role": "developer",  # or "system"
            "content": cl.user_session.get("dev_prompt") or DEV_PROMPT,
        })
    print(dev_input + input_messages)
    stream = await client.responses.create(
        model="gpt-5-mini",
        reasoning={"effort": "minimal"},
        input=dev_input + input_messages,  # Only current turn messages
        instructions="Never ask clarifying questions. Use the tools when needed.",
        stream=True,
        store=True,
        tools=tools,
        tool_choice="auto",
        **({"previous_response_id": prev_id} if prev_id else {}),
    )
    ans = cl.Message(author="Assistant", content="")
    await ans.send()
    calls, resp_id = [], None
    assistant_text = ""

    async for ev in stream:
        if ev.type == "response.created":
            resp_id = ev.response.id
        elif ev.type == "response.output_item.added" and ev.item.type == "function_call":
            calls.append(
                {
                    "id": ev.item.id,
                    "call_id": ev.item.call_id,
                    "name": ev.item.name,
                    "arguments": "",
                }
            )
        elif ev.type == "response.function_call_arguments.delta":
            next(c for c in calls if c["id"] == ev.item_id)["arguments"] += ev.delta
        elif ev.type == "response.output_text.delta":
            assistant_text += ev.delta
            await ans.stream_token(ev.delta)

    await ans.update()

    if assistant_text.strip():
        full_history = cl.user_session.get("full_conversation_history")
        full_history.append({"role": "assistant", "content": assistant_text})
        cl.user_session.set("full_conversation_history", full_history)

    # Handle incomplete responses
    try:
        final_response = stream.get_final_response()
        if (
            hasattr(final_response, "status")
            and final_response.status == "incomplete"
            and final_response.incomplete_details.reason == "max_output_tokens"
        ):
            await cl.Message(
                content="⚠️ Response was truncated due to length limits",
                author="System",
            ).send()
    except Exception:
        pass

    return resp_id, calls


@cl.on_message
async def _on_msg(m: cl.Message):
    full_history = cl.user_session.get("full_conversation_history")

    if not full_history:
        full_history.append(
            {"role": "developer", "content": cl.user_session.get("dev_prompt") or DEV_PROMPT}
        )

    full_history.append({"role": "user", "content": m.content})
    cl.user_session.set("full_conversation_history", full_history)

    current_turn_messages = [{"role": "user", "content": m.content}]
    prev_response_id = cl.user_session.get("previous_response_id")

    for _ in range(MAX_ITER):
        resp_id, calls = await _ask_gpt5(current_turn_messages, prev_response_id)

        if not calls:
            break

        for call in calls:
            await call_function_tool(call, full_history)

        tool_results = cl.user_session.get("tool_results")
        current_turn_messages = [
            {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": tool_results[call["call_id"]],
            }
            for call in calls
        ]
        prev_response_id = resp_id

    cl.user_session.set("full_conversation_history", full_history)
    cl.user_session.set("previous_response_id", resp_id)

    await show_full_conversation([{"role": "user", "content": m.content}], full_history)
