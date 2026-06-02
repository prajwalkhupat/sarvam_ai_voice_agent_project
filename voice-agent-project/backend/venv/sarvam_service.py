from sarvamai import SarvamAI
from dotenv import load_dotenv
import os

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv(
        "SARVAM_API_KEY"
    )
)

def ask_sarvam(messages):

    response = client.chat.completions(
        model="sarvam-30b",
        messages=messages
    )

    return (
        response
        .choices[0]
        .message
        .content
    )