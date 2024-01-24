from enum import auto, Enum
import json
import dataclasses
from typing import List
import aiohttp
from PIL import Image
import io
import os

import chainlit as cl
from chainlit.input_widget import Select, Slider

CONTROLLER_URL = os.environ.get("LLAVA_CONTROLLER_URL")


class SeparatorStyle(Enum):
    """Different separator style."""

    SINGLE = auto()
    TWO = auto()
    MPT = auto()
    PLAIN = auto()
    LLAMA_2 = auto()


@dataclasses.dataclass
class Conversation:
    """A class that keeps all conversation history."""

    system: str
    roles: List[str]
    messages: List[List[str]]
    offset: int
    sep_style: SeparatorStyle = SeparatorStyle.SINGLE
    sep: str = "###"
    sep2: str = None
    version: str = "Unknown"

    skip_next: bool = False

    def get_prompt(self):
        messages = self.messages
        if self.sep_style == SeparatorStyle.SINGLE:
            ret = self.system + self.sep
            for role, message in messages:
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += role + ": " + message + self.sep
                else:
                    ret += role + ":"
        elif self.sep_style == SeparatorStyle.TWO:
            seps = [self.sep, self.sep2]
            ret = self.system + seps[0]
            for i, (role, message) in enumerate(messages):
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += role + ": " + message + seps[i % 2]
                else:
                    ret += role + ":"
        elif self.sep_style == SeparatorStyle.MPT:
            ret = self.system + self.sep
            for role, message in messages:
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += role + message + self.sep
                else:
                    ret += role
        elif self.sep_style == SeparatorStyle.LLAMA_2:
            wrap_sys = lambda msg: f"<<SYS>>\n{msg}\n<</SYS>>\n\n"
            wrap_inst = lambda msg: f"[INST] {msg} [/INST]"
            ret = ""

            for i, (role, message) in enumerate(messages):
                if i == 0:
                    assert message, "first message should not be none"
                    assert role == self.roles[0], "first message should come from user"
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    if i == 0:
                        message = wrap_sys(self.system) + message
                    if i % 2 == 0:
                        message = wrap_inst(message)
                        ret += self.sep + message
                    else:
                        ret += " " + message + " " + self.sep2
                else:
                    ret += ""
            ret = ret.lstrip(self.sep)
        elif self.sep_style == SeparatorStyle.PLAIN:
            seps = [self.sep, self.sep2]
            ret = self.system
            for i, (role, message) in enumerate(messages):
                if message:
                    if type(message) is tuple:
                        message, _, _ = message
                    ret += message + seps[i % 2]
                else:
                    ret += ""
        else:
            raise ValueError(f"Invalid style: {self.sep_style}")

        return ret

    def append_message(self, role, message):
        self.messages.append([role, message])

    def get_images(self, return_pil=False):
        images = []
        for i, (role, msg) in enumerate(self.messages[self.offset :]):
            if i % 2 == 0:
                if type(msg) is tuple:
                    import base64
                    from io import BytesIO
                    from PIL import Image

                    msg, image, image_process_mode = msg
                    if image == None:
                        continue
                    if image_process_mode == "Pad":

                        def expand2square(pil_img, background_color=(122, 116, 104)):
                            width, height = pil_img.size
                            if width == height:
                                return pil_img
                            elif width > height:
                                result = Image.new(
                                    pil_img.mode, (width, width), background_color
                                )
                                result.paste(pil_img, (0, (width - height) // 2))
                                return result
                            else:
                                result = Image.new(
                                    pil_img.mode, (height, height), background_color
                                )
                                result.paste(pil_img, ((height - width) // 2, 0))
                                return result

                        image = expand2square(image)
                    elif image_process_mode in ["Default", "Crop"]:
                        pass
                    elif image_process_mode == "Resize":
                        image = image.resize((336, 336))
                    else:
                        raise ValueError(
                            f"Invalid image_process_mode: {image_process_mode}"
                        )
                    max_hw, min_hw = max(image.size), min(image.size)
                    aspect_ratio = max_hw / min_hw
                    max_len, min_len = 800, 400
                    shortest_edge = int(min(max_len / aspect_ratio, min_len, min_hw))
                    longest_edge = int(shortest_edge * aspect_ratio)
                    W, H = image.size
                    if longest_edge != max(image.size):
                        if H > W:
                            H, W = longest_edge, shortest_edge
                        else:
                            H, W = shortest_edge, longest_edge
                        image = image.resize((W, H))
                    if return_pil:
                        images.append(image)
                    else:
                        buffered = BytesIO()
                        image.save(buffered, format="PNG")
                        img_b64_str = base64.b64encode(buffered.getvalue()).decode()
                        images.append(img_b64_str)
        return images

    def copy(self):
        return Conversation(
            system=self.system,
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            offset=self.offset,
            sep_style=self.sep_style,
            sep=self.sep,
            sep2=self.sep2,
            version=self.version,
        )

    def dict(self):
        if len(self.get_images()) > 0:
            return {
                "system": self.system,
                "roles": self.roles,
                "messages": [
                    [x, y[0] if type(y) is tuple else y] for x, y in self.messages
                ],
                "offset": self.offset,
                "sep": self.sep,
                "sep2": self.sep2,
            }
        return {
            "system": self.system,
            "roles": self.roles,
            "messages": self.messages,
            "offset": self.offset,
            "sep": self.sep,
            "sep2": self.sep2,
        }


default_conversation = Conversation(
    system="A chat between a curious human and an artificial intelligence assistant. "
    "The assistant gives helpful, detailed, and polite answers to the human's questions.",
    roles=("USER", "ASSISTANT"),
    version="v1",
    messages=(),
    offset=0,
    sep_style=SeparatorStyle.TWO,
    sep=" ",
    sep2="</s>",
)


headers = {"User-Agent": "LLaVA Client"}
image_process_mode = "Default"


async def request(conversation: Conversation, settings):
    pload = {
        "model": settings["model"],
        "prompt": conversation.get_prompt(),
        "temperature": settings["temperature"],
        "top_p": settings["top_p"],
        "max_new_tokens": int(settings["max_token"]),
        "stop": conversation.sep
        if conversation.sep_style in [SeparatorStyle.SINGLE, SeparatorStyle.MPT]
        else conversation.sep2,
    }

    pload["images"] = conversation.get_images()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            CONTROLLER_URL + "/worker_generate_stream",
            headers=headers,
            data=json.dumps(pload),
            timeout=10,
        ) as response:
            chainlit_message = cl.Message(content="")
            async for chunk in response.content.iter_any():
                for json_str in chunk.decode().split("\0"):
                    if json_str:
                        data = json.loads(json_str)

                        if data["error_code"] == 0:
                            output = data["text"][len(pload["prompt"]) :].strip()
                            conversation.messages[-1][-1] = output + "▌"
                            await chainlit_message.stream_token(
                                output, is_sequence=True
                            )
                        else:
                            output = (
                                data["text"] + f" (error_code: {data['error_code']})"
                            )
                            conversation.messages[-1][-1] = output
                            chainlit_message.content = output
            await chainlit_message.send()
    return conversation


@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Model",
                values=["llava-v1.5-13b"],
                initial_index=0,
            ),
            Slider(
                id="temperature",
                label="Temperature",
                initial=0,
                min=0,
                max=1,
                step=0.1,
            ),
            Slider(
                id="top_p",
                label="Top P",
                initial=0.7,
                min=0,
                max=1,
                step=0.1,
            ),
            Slider(
                id="max_token",
                label="Max output tokens",
                initial=512,
                min=0,
                max=1024,
                step=64,
            ),
        ]
    ).send()

    conversation = default_conversation.copy()

    cl.user_session.set("conversation", conversation)
    cl.user_session.set("settings", settings)


@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set("settings", settings)


@cl.on_message
async def main(message: cl.Message):
    image = next(
        (
            Image.open(file.path)
            for file in message.elements or []
            if "image" in file.mime and file.path is not None
        ),
        None,
    )

    conv = cl.user_session.get("conversation")  # type: Conversation
    settings = cl.user_session.get("settings")

    if image:
        if len(conv.get_images(return_pil=True)) > 0:
            # reset
            conv = default_conversation.copy()
        text = message.content[:1200]
        if "<image>" not in text:
            text = "<image>\n" + text
    else:
        text = message.content[:1536]

    conv_message = (text, image, image_process_mode)
    conv.append_message(conv.roles[0], conv_message)
    conv.append_message(conv.roles[1], None)

    conv = await request(conv, settings)

    cl.user_session.set("conversation", conv)
