import json
from openai import AsyncOpenAI
import asyncio
import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

tools = [
    {"type": "code_interpreter"},
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    },
                },
                "required": ["location", "format", "num_days"],
            },
        },
    },
]


def get_current_weather(location: str, format: str):
    # return dummy weather
    return "The current weather in {} is {} degrees {}".format(location, 20, format)


def get_n_day_weather_forecast(location: str, format: str, num_days: int):
    # return dummy weather
    return "The weather forecast for the next {} days in {} is {} degrees {}".format(
        num_days, location, 20, format
    )


tool_map = {
    "get_current_weather": get_current_weather,
    "get_n_day_weather_forecast": get_n_day_weather_forecast,
}


async def create():
    # ... your existing create function code ...

    instructions = """You are a personal math tutor. Write and run code to answer math questions.
Enclose math expressions in $$ (this is helpful to display latex). Example:
```
Given a formula below $$ s = ut + \frac{1}{2}at^{2} $$ Calculate the value of $s$ when $u = 10\frac{m}{s}$ and $a = 2\frac{m}{s^{2}}$ at $t = 1s$
```

You can also answer weather questions!
"""

    assistant = await client.beta.assistants.create(
        name="Math Tutor And Weather Bot",
        instructions=instructions,
        tools=tools,
        model="gpt-4-1106-preview",
    )
    assistant_name = "math_tutor_and_weather_bot"
    # append key value pair to assistants.json

    def load_or_create_json(filename):
        try:
            return json.load(open(filename, "r"))
        except FileNotFoundError:
            return {}

    assistant_dict = load_or_create_json("assistants.json")
    assistant_dict[assistant_name] = assistant.id
    json.dump(assistant_dict, open("assistants.json", "w"))

if __name__ == "__main__":
    asyncio.run(create())
