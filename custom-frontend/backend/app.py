from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from chainlit.user import User
from chainlit.utils import mount_chainlit
from chainlit.server import _authenticate_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/custom-auth")
async def custom_auth(request: Request):
    # Verify the user's identity with custom logic.
    user = User(identifier="Test User")

    return await _authenticate_user(request, user)


mount_chainlit(app=app, target="cl_app.py", path="/chainlit")