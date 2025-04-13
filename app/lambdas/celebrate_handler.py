from fastapi import FastAPI, Request
import os, logging, httpx

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

@app.post("/celebrate")
async def celebrate_win(req: Request):
    data = await req.json()
    achievement = data.get("achievement", "")
    prompt = f"Write a short, energetic, and inspiring celebration message for someone who achieved this: {achievement}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            result = response.json()
            return {"reply": result["candidates"][0]["content"]["parts"][0]["text"]}
    except Exception as e:
        logging.error("Celebrate win error: %s", e)
        return {"reply": "Error generating celebration message"}
