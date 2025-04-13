from fastapi import FastAPI, Request
import os, logging, httpx

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

@app.post("/ask-reply")
async def ask_reply(req: Request):
    data = await req.json()
    question = data.get("question")
    if not question:
        return {"error": "Missing 'question' field."}
    prompt = f"Give a short, kind, and practical response (max 40 words) to help this mentee: '{question}'"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            result = response.json()
            return {"reply": result["candidates"][0]["content"]["parts"][0]["text"]}
    except Exception as e:
        logging.error("Ask reply error: %s", e)
        return {"reply": "Error generating ask reply"}
