from fastapi import FastAPI
import os, random, logging, httpx

app = FastAPI()

TEMPLATES = [
    "Write a short, calming affirmation for someone building confidence in their tech journey. Keep it under 20 words.",
    "Generate a motivational, mentor-style affirmation that inspires someone learning, failing, and growing in tech. Max 20 words.",
    "Give a daily positive affirmation for someone overcoming self-doubt while learning to code. Warm and hopeful tone. Max 30 words."
]

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

@app.post("/affirmation")
async def affirmation():
    prompt = random.choice(TEMPLATES)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            result = response.json()
            return {"reply": result["candidates"][0]["content"]["parts"][0]["text"]}
    except Exception as e:
        logging.error("Error generating affirmation: %s", e)
        return {"reply": "Error generating affirmation"}