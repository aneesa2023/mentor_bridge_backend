from fastapi import FastAPI, Request
import httpx, os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.get("/")
def home():
    return {"message": "MentorBridge backend running 🎉"}

@app.post("/generate")
async def generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        result = response.json()

    reply = result["candidates"][0]["content"]["parts"][0]["text"]
    return {"reply": reply}
