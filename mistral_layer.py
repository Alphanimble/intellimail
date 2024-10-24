import os
from dotenv import load_dotenv
from mistralai import Mistral
import psgs

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("MISTRAL_API_KEY")

# Initialize Mistral client
mistral_client = Mistral(api_key=api_key)


def process_prompt(text):
    chat_response = mistral_client.agents.complete(
        agent_id="ag:66d97af1:20241022:untitled-agent:3067016b",
        messages=[
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    print(chat_response.choices[0].message.content)
    return chat_response.choices[0].message.content


# text=input("enter your prompt:  ")


def execute_response(query):
    conn = psgs.connect_to_db("mails", "root", "root")
    if conn:
        return psgs.execute_query(conn, query)
