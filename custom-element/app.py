import chainlit as cl


@cl.action_callback("handle_file_selection")
async def handle_file_selection(action):
    selected_files = action.payload.get("selected_files", [])
    msg = cl.Message(content=f"Selected files : {'.'.join(selected_files)}")
    await msg.send()

@cl.on_chat_start
async def start():
    files = ["files/minimal-document.pdf", "files/pdflatex-image.pdf"]
    pdf_selector = cl.CustomElement(
        name="PdfSelector", 
        props={
            "files": files,
        },
    )
    await cl.Message(content=f"Choose files: ", elements=[pdf_selector]).send()
