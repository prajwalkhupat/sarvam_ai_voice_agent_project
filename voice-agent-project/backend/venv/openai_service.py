from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

def ask_gpt(user_text):

    response = (
        client.chat.completions.create(
            model=
            "llama-3.3-70b-versatile",

            messages=[
                {
                    "role":
                    "system",

                    "content":
                    """
                    You are a helpful
                    voice assistant.
                    Keep answers short.
                    """
                },
                {
                    "role":
                    "user",

                    "content":
                    user_text
                }
            ]
        )
    )

    return (
        response
        .choices[0]
        .message
        .content
    )