import os
import chainlit as cl


async def need_file_upload():
    """
    When the user's question mentions handling files, you need to upload files, you can call this function.
    Parameters: None
    """
    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')
    files = await cl.AskFileMessage(
        content="Please upload a text file to begin!",
        max_size_mb=10,
        accept=[
            "text/plain",
            "image/png",
            "image/jpeg",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # for .xlsx files
            "application/vnd.ms-excel",  # for .xls files
            "text/csv",  # for .csv files
            # More MIME types here as needed.
        ]).send()
    file = files[0]
    
    # 保存文件到paths目录下
    # 判断paths目录是否存在
    file_path = f"./tmp/{file.name}"
    # 保存文件
    content = file.content
    file_name = file.name
    file_type = file.type
    # 保存文件
    # content是bytes类型
    with open(file_path, "wb") as f:
        f.write(content)
    return {
        'type': 'file',
        'path': file_path,
        'name': file_name,
        'file_type': file_type
    }


async def show_images(paths: str):
    """
    If your return contains images in png or jpg format, you can call this function to display the images.
    Parameters: paths: The paths of the images as a comma-separated string.(required)
    """
    path_list = paths.split(',')
    elments = []
    for i, path in enumerate(path_list):
        tmp_image = cl.Image(name=f"image{i}",
                             path=path.strip(),
                             display="inline")
        tmp_image.size = "large"
        elments.append(tmp_image)

    await cl.Message(content="Look at these local images!",
                     elements=elments).send()  # type: ignore

    return {'description': '图片已经显示成功了，下面的回复中不再需要展示它了'}