"""
Chainlit animated waiting indicator - optimized version
"""

import chainlit as cl
import asyncio
from typing import List

async def send_animated_message(
    base_msg: str,
    frames: List[str],
    interval: float = 0.8
    ) -> None:
    """Display animated message with minimal resource usage"""
    msg = cl.Message(content=base_msg)
    await msg.send()
    
    progress = 0
    bar_length = 12  # Optimal length for progress bar
    
    try:
        while True:
            # Efficient progress calculation
            current_frame = frames[progress % len(frames)]
            progress_bar = ("▣" * (progress % bar_length)).ljust(bar_length, "▢")
            
            # Single update operation - overwrite entire content
            new_content = f"{current_frame} {base_msg}\n{progress_bar}"
            msg.content = new_content
            await msg.update()
            
            progress += 1
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        msg.content = base_msg
        await msg.update()  # Final static message

@cl.on_message
async def main(message: cl.Message) -> None:
    """Optimized message handler"""
    if message.content.lower() == "test animation":
        animation_task = asyncio.create_task(
            send_animated_message(
                "Processing (30s)...",
                ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
                0.8
            )
        )
        
        await asyncio.sleep(30)
        animation_task.cancel()
        await animation_task
        
        await cl.Message(content="Done!").send()
    else:
        await cl.Message(content="Send 'test animation'").send()