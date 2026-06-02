from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import BaseModel

from openai_service import (
    ask_gpt
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():

    return {
        "message":
        "Backend Running"
    }


@app.post("/chat")
def chat(data: ChatRequest):

    user_message = data.message

    ai_response = ask_gpt(
        user_message
    )

    return {
        "user_message":
        user_message,

        "ai_response":
        ai_response
    }