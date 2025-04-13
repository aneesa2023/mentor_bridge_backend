from fastapi import FastAPI, Request
import os, logging, httpx

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

TEMPLATE = "Write a warm and confident intro message from {name} who wants to {goal} and {fun}."

@app.post("/intro-message")
async def intro_message(req: Request):
    data = await req.json()
    prompt = TEMPLATE.format(
        name=data.get("name", "a mentee"),
        goal=data.get("goal", "learn Flutter"),
        fun=data.get("fun", "enjoys anime")
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            result = response.json()
            return {"reply": result["candidates"][0]["content"]["parts"][0]["text"]}
    except Exception as e:
        logging.error("Error generating intro message: %s", e)
        return {"reply": "Error generating intro message"}