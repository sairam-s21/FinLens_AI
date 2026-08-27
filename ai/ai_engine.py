import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Your system prompt forces Llama-3 to act as a specialized fine-tuned parser
SYSTEM_PROMPT = """You are a specialized financial risk analyzer. 
Analyze the receipt text and output ONLY a raw JSON object formatted exactly as:
{"risk_score": <number 0-100>, "audit_flags": [<string>, ...]}"""

def analyze_receipt(receipt_text: str):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # Free tier model on Groq
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": receipt_text}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)