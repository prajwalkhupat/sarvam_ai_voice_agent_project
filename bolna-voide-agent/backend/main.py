from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOLNA_API_KEY = os.getenv("BOLNA_API_KEY")
AGENT_ID = os.getenv("AGENT_ID")

print("AGENT_ID =", AGENT_ID)
print("API KEY FOUND =", bool(BOLNA_API_KEY))


@app.get("/")
def home():
    return {
        "message": "Backend Running"
    }


@app.get("/latest-customer")
def latest_customer():

    try:

        headers = {
            "Authorization": f"Bearer {BOLNA_API_KEY}"
        }

        url = f"https://api.bolna.ai/agents/{AGENT_ID}/executions"

        print("\n====================")
        print("REQUEST URL:", url)

        response = requests.get(
            url,
            headers=headers
        )

        print("STATUS CODE:", response.status_code)
        print("RESPONSE TEXT:")
        print(response.text)
        print("====================\n")

        return {
            "status_code": response.status_code,
            "response": response.text
        }

    except Exception as e:

        import traceback

        print(traceback.format_exc())

        return {
            "error": str(e)
        }