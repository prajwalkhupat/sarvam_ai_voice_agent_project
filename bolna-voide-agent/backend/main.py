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

campaign_running = False
campaign_results = []


# =====================================================
# Extract Customer Data
# =====================================================

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

    hindi_match = re.search(
        r"आपका नाम\s+(.*?),\s*उम्र\s+(\d+).*?फोन नंबर\s+(\d{10})",
        transcript,
        re.DOTALL
    )

    if english_match:
        customer["name"] = english_match.group(1).strip()
        customer["age"] = english_match.group(2).strip()
        customer["phone"] = english_match.group(3).strip()

    elif hindi_match:
        customer["name"] = hindi_match.group(1).strip()
        customer["age"] = hindi_match.group(2).strip()
        customer["phone"] = hindi_match.group(3).strip()

    return customer


# =====================================================
# Make Call
# =====================================================

def make_call(phone):

    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "agent_id": AGENT_ID,
        "recipient_phone_number": phone
    }

    print(f"\n📞 Calling {phone}")

    response = requests.post(
        "https://api.bolna.ai/call",
        json=payload,
        headers=headers
    )

    print("CALL RESPONSE:")
    print(response.text)

    data = response.json()

    execution_id = (
        data.get("execution_id")
        or data.get("id")
    )

    return execution_id


# =====================================================
# Wait Until Call Completes
# =====================================================

def wait_for_execution(execution_id):

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

        print(
            f"Execution: {execution_id} | Status: {status}"
        )

        if status in [
            "completed",
            "busy",
            "failed",
            "rejected",
            "no-answer",
            "canceled"
        ]:
            return data

        time.sleep(5)


# =====================================================
# Campaign Worker
# =====================================================

def process_campaign(numbers):

    global campaign_running
    global campaign_results

    retry_numbers = []

    print("\n========================")
    print("STARTING CAMPAIGN")
    print("========================")

    # --------------------------------
    # First Round
    # --------------------------------

    for phone in numbers:

        try:

            execution_id = make_call(phone)

            if not execution_id:

                campaign_results.append({
                    "phone": phone,
                    "status": "execution_id_not_found"
                })

                continue

            result = wait_for_execution(
                execution_id
            )

            status = result.get("status")

            print(
                f"{phone} => {status}"
            )

            if status == "completed":

                transcript = result.get(
                    "transcript",
                    ""
                )

                customer = extract_customer(
                    transcript
                )

                campaign_results.append({
                    "execution_id": execution_id,
                    "phone": phone,
                    "status": "completed",
                    "name": customer["name"],
                    "age": customer["age"]
                })

            else:

                campaign_results.append({
                    "execution_id": execution_id,
                    "phone": phone,
                    "status": status
                })

                retry_numbers.append(phone)

        except Exception as e:

            campaign_results.append({
                "phone": phone,
                "status": f"error: {str(e)}"
            })

    # --------------------------------
    # Retry Round
    # --------------------------------

    if retry_numbers:

        print("\n========================")
        print("RETRYING CUSTOMERS")
        print("========================")

    for phone in retry_numbers:

        try:

            execution_id = make_call(phone)

            if not execution_id:
                continue

            result = wait_for_execution(
                execution_id
            )

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
                    "execution_id": execution_id,
                    "phone": phone,
                    "status": "completed_retry",
                    "name": customer["name"],
                    "age": customer["age"]
                })

            else:

                campaign_results.append({
                    "execution_id": execution_id,
                    "phone": phone,
                    "status": "failed_after_retry"
                })

        except Exception as e:

            campaign_results.append({
                "phone": phone,
                "status": f"retry_error: {str(e)}"
            })

    campaign_running = False

    print("\n========================")
    print("CAMPAIGN COMPLETED")
    print("========================")


# =====================================================
# Routes
# =====================================================

@app.get("/")
def home():

    return {
        "message": "Backend Running"
    }


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

    numbers = payload.get(
        "numbers",
        []
    )

    print("\nRECEIVED NUMBERS:")
    print(numbers)

    if not numbers:

        return {
            "success": False,
            "message": "No phone numbers received"
        }

    campaign_running = True

    worker = threading.Thread(
        target=process_campaign,
        args=(numbers,)
    )

    worker.start()

    return {
        "success": True,
        "total_numbers": len(numbers),
        "message": "Campaign Started"
    }


@app.get("/campaign-results")
def campaign_results_api():

    return {
        "running": campaign_running,
        "total": len(campaign_results),
        "results": campaign_results
    }