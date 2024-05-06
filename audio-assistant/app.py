import os
from io import BytesIO
import base64
import httpx

from openai import AsyncOpenAI

from chainlit.element import ElementBased
import chainlit as cl

cl.instrument_openai()

client = AsyncOpenAI()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")

if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
    raise ValueError("ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID must be set")


# Function to encode an image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@cl.step(type="tool")
async def speech_to_text(audio_file):
    response = await client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )

    return response.text


@cl.step(type="tool")
async def generate_text_answer(transcription, images):
    if images:
        # Only process the first 3 images
        images = images[:3]

        images_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image.mime};base64,{encode_image(image.path)}"
                },
            }
            for image in images
        ]

        model = "gpt-4-turbo"
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": transcription}, *images_content],
            }
        ]
    else:
        model = "gpt-3.5-turbo"
        messages = [{"role": "user", "content": transcription}]

    response = await client.chat.completions.create(
        messages=messages, model=model, temperature=0.3
    )

    return response.choices[0].message.content


@cl.step(type="tool")
async def text_to_speech(text: str, mime_type: str):
    CHUNK_SIZE = 1024

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
    "Accept": mime_type,
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()  # Ensure we notice bad responses

        buffer = BytesIO()
        buffer.name = f"output_audio.{mime_type.split('/')[1]}"

        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
            if chunk:
                buffer.write(chunk)
        
        buffer.seek(0)
        return buffer.name, buffer.read()
        

@cl.on_chat_start
async def start():
    await cl.Message(
        content="Welcome to the Chainlit audio example. Press `P` to talk!"
    ).send()


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    if chunk.isStart:
        buffer = BytesIO()
        # This is required for whisper to recognize the file type
        buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
        # Initialize the session for a new audio stream
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)

    # TODO: Use Gladia to transcribe chunks as they arrive would decrease latency
    # see https://docs-v1.gladia.io/reference/live-audio
    
    # For now, write the chunks to a buffer and transcribe the whole audio at the end
    cl.user_session.get("audio_buffer").write(chunk.data)


@cl.on_audio_end
async def on_audio_end(elements: list[ElementBased]):
    # Get the audio buffer from the session
    audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)  # Move the file pointer to the beginning
    audio_file = audio_buffer.read()
    audio_mime_type: str = cl.user_session.get("audio_mime_type")

    input_audio_el = cl.Audio(
        mime=audio_mime_type, content=audio_file, name=audio_buffer.name
    )
    await cl.Message(
        author="You", 
        type="user_message",
        content="",
        elements=[input_audio_el, *elements]
    ).send()
    
    answer_message = await cl.Message(content="").send()
    
    whisper_input = (audio_buffer.name, audio_file, audio_mime_type)
    transcription = await speech_to_text(whisper_input)

    images = [file for file in elements if "image" in file.mime]

    text_answer = await generate_text_answer(transcription, images)
    
    output_name, output_audio = await text_to_speech(text_answer, audio_mime_type)
    
    output_audio_el = cl.Audio(
        name=output_name,
        auto_play=True,
        mime=audio_mime_type,
        content=output_audio,
    )
    
    answer_message.elements = [output_audio_el]
    await answer_message.update()

