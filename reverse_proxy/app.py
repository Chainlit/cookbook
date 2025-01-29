from fastapi import FastAPI, Request
from chainlit.utils import mount_chainlit

app = FastAPI()


@app.get("/app")
def read_main(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}


mount_chainlit(app=app, target="clapp.py", path="/chainlit")
