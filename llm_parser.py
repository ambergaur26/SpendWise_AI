import os
import json
from dotenv import load_dotenv
from groq import Groq
import re


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expense tracking assistant.

Extract transaction details from user input.
Return ONLY valid JSON in this format:

{
  "type": "income" or "expense",
  "amount": number,
  "category": string,
  "description": string
}

Do not return any explanation.
"""

def extract_transaction(user_message: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    output = response.choices[0].message.content

    output = response.choices[0].message.content.strip()


    match = re.search(r"\{.*\}", output, re.DOTALL)

    if not match:
        raise ValueError(f"Invalid LLM output: {output}")

    clean_json = match.group()

    return json.loads(clean_json)