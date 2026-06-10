from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import requests
import os
import re
import time
import threading

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

campaign_results = []
campaign_running = False


def extract_customer(transcript):

    customer = {
        "name": "",
        "age": "",
        "phone": ""
    }

    if not transcript:
        return customer

    english_match = re.search(
        r"Your name is\s+(.*?),\s*age is\s+(\d+),\s*and phone number is\s+(\d{10})",
        transcript,
        re.IGNORECASE | re.DOTALL
    )

    if english_match:
        customer["name"] = english_match.group(1).strip()
        customer["age"] = english_match.group(2).strip()
        customer["phone"] = english_match.group(3).strip()

    return customer


def get_execution(execution_id):

    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}"
    }

    while True:

        response = requests.get(
            f"https://api.bolna.ai/executions/{execution_id}",
            headers=headers
        )

        data = response.json()

        status = data.get("status")

        print("STATUS:", status)

        if status in ["completed", "busy", "failed"]:
            return data

        time.sleep(5)


def make_call(phone):

    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "agent_id": AGENT_ID,
        "recipient_phone_number": phone
    }

    response = requests.post(
        "https://api.bolna.ai/call",
        json=payload,
        headers=headers
    )

    data = response.json()

    execution_id = (
        data.get("execution_id")
        or data.get("id")
    )

    return execution_id


def process_campaign(numbers):

    global campaign_running
    global campaign_results

    retry_list = []

    for phone in numbers:

        execution_id = make_call(phone)

        if not execution_id:
            continue

        result = get_execution(execution_id)

        status = result.get("status")

        if status == "completed":

            transcript = result.get(
                "transcript",
                ""
            )

            customer = extract_customer(
                transcript
            )

            campaign_results.append({
                "phone": phone,
                "status": "completed",
                **customer
            })

        else:

            campaign_results.append({
                "phone": phone,
                "status": status
            })

            retry_list.append(phone)

    print("Retrying Busy Customers")

    for phone in retry_list:

        execution_id = make_call(phone)

        result = get_execution(execution_id)

        status = result.get("status")

        if status == "completed":

            transcript = result.get(
                "transcript",
                ""
            )

            customer = extract_customer(
                transcript
            )

            campaign_results.append({
                "phone": phone,
                "status": "completed_retry",
                **customer
            })

        else:

            campaign_results.append({
                "phone": phone,
                "status": "failed_after_retry"
            })

    campaign_running = False


@app.get("/")
def home():
    return {"message": "Backend Running"}


@app.post("/start-campaign")
def start_campaign(payload: dict):

    global campaign_running
    global campaign_results

    if campaign_running:
        return {
            "success": False,
            "message": "Campaign already running"
        }

    campaign_results = []

    numbers = payload["numbers"]

    campaign_running = True

    thread = threading.Thread(
        target=process_campaign,
        args=(numbers,)
    )

    thread.start()

    return {
        "success": True
    }


@app.get("/campaign-results")
def campaign_results_api():

    return {
        "running": campaign_running,
        "results": campaign_results
    }