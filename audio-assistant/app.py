from io import BytesIO
import base64

from openai import AsyncOpenAI

from chainlit.element import ElementBased
import chainlit as cl

client = AsyncOpenAI()


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
        buffer.name = f"audio.{chunk.mimeType.split('/')[1]}"
        # Initialize the session for a new audio stream
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)

    # TODO: Transcribing chunks as they arrive would decrease latency
    # Instead we write the chunks to a buffer and transcribe the whole audio at the end for now
    cl.user_session.get("audio_buffer").write(chunk.data)


@cl.on_audio_end
async def on_audio_end(elements: list[ElementBased]):
    # Get the audio buffer from the session
    audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)  # Move the file pointer to the beginning
    audio_file = audio_buffer.read()
    audio_mime_type: str = cl.user_session.get("audio_mime_type")

    audio_el = cl.Audio(
        mime=audio_mime_type, content=audio_file, name=audio_buffer.name
    )
    await cl.Message(
        content="Received the following audio request:", elements=[audio_el, *elements]
    ).send()

    answer_message = await cl.Message(content="").send()

    whisper_input = (audio_buffer.name, audio_file, audio_mime_type)
    transcription = await speech_to_text(whisper_input)

    images = [file for file in elements if "image" in file.mime]

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

    stream = await client.chat.completions.create(
        messages=messages, stream=True, model=model, temperature=0.3
    )

    # TODO: We could synthetize the audio from the text response and send it back to the user with auto_play=True

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await answer_message.stream_token(token)

    await answer_message.update()
