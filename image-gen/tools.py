import io
import os

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from langchain.tools import StructuredTool, Tool
from PIL import Image
from stability_sdk import client

import chainlit as cl

os.environ["STABILITY_HOST"] = "grpc.stability.ai:443"


def get_image_name():
    image_count = cl.user_session.get("image_count")
    if image_count is None:
        image_count = 0
    else:
        image_count += 1

    cl.user_session.set("image_count", image_count)

    return f"image-{image_count}"


def _generate_image(prompt: str, init_image=None):
    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key=os.environ["STABILITY_KEY"],  # API Key reference.
        verbose=True,  # Print debug messages.
        engine="stable-diffusion-xl-beta-v2-2-2",  # Set the engine to use for generation.
        # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
        # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0
    )

    start_schedule = 0.8 if init_image else 1

    cl_chat_settings = cl.user_session.get("chat_settings")

    # Set up our initial generation parameters.
    answers = stability_api.generate(
        prompt=prompt,
        init_image=init_image,
        start_schedule=start_schedule,
        seed=992446758,  # If a seed is provided, the resulting generated image will be deterministic.
        # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
        # Note: This isn't quite the case for CLIP Guided generations, which we tackle in the CLIP Guidance documentation.
        steps=int(cl_chat_settings["SAI_Steps"]),  # Amount of inference steps performed on image generation. Defaults to 30.
        cfg_scale=cl_chat_settings["SAI_Cfg_Scale"],  # Influences how strongly your generation is guided to match your prompt.
        # Setting this value higher increases the strength in which it tries to match your prompt.
        # Defaults to 7.0 if not specified.
        width=int(cl_chat_settings["SAI_Width"]),  # Generation width, defaults to 512 if not included.
        height=int(cl_chat_settings["SAI_Height"]),  # Generation height, defaults to 512 if not included.
        samples=1,  # Number of images to generate, defaults to 1 if not included.
        sampler=generation.SAMPLER_K_EULER  # Choose which sampler we want to denoise our generation with.
        # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
        # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
    )

    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save generated images.
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                raise ValueError(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again."
                )
            if artifact.type == generation.ARTIFACT_IMAGE:
                name = get_image_name()
                cl.user_session.set(name, artifact.binary)
                cl.user_session.set("generated_image", name)
                return name
            else:
                raise ValueError(
                    f"Your request did not generate an image. Please modify the prompt and try again. Finish reason: {artifact.finish_reason}"
                )


def generate_image(prompt: str):
    image_name = _generate_image(prompt)
    return f"Here is {image_name}."


def edit_image(init_image_name: str, prompt: str):
    init_image_bytes = cl.user_session.get(init_image_name)
    if init_image_bytes is None:
        raise ValueError(f"Could not find image `{init_image_name}`.")

    init_image = Image.open(io.BytesIO(init_image_bytes))
    image_name = _generate_image(prompt, init_image)

    return f"Here is {image_name} based on {init_image_name}."


generate_image_tool = Tool.from_function(
    func=generate_image,
    name="GenerateImage",
    description="Useful to create an image from a text prompt.",
    return_direct=True,
)

edit_image_tool = StructuredTool.from_function(
    func=edit_image,
    name="EditImage",
    description="Useful to edit an image with a prompt. Works well with commands such as 'replace', 'add', 'change', 'remove'.",
    return_direct=True,
)
