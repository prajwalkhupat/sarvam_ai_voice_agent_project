from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from memory import conversation_history
from sarvam_service import ask_sarvam

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Backend Running"
    }

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(data: ChatRequest):

    print("User:", data.message)

    conversation_history.append({
        "role": "user",
        "content": data.message
    })

    try:

        ai_response = ask_sarvam(
            conversation_history
        )

        conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })

        print(
            "AI:",
            ai_response
        )

        return {
            "success": True,
            "ai_response": ai_response
        }

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return {
            "success": False,
            "error": str(e)
        }

@app.get("/memory")
def memory():
    return {
        "messages":
        conversation_history
    }

@app.delete("/memory")
def clear_memory():

    conversation_history.clear()

    return {
        "success": True,
        "message": "Memory Cleared"
    }