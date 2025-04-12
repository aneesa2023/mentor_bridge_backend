from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv
from httpx import HTTPError, TimeoutException
from json.decoder import JSONDecodeError
import logging
import traceback
import random

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"  # or gemini-2.0-pro
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Prompt Templates
TEMPLATES = {
    "affirmation_1": "Write a short, calming affirmation for someone building confidence in their tech journey. Keep it under 20 words.",
    "affirmation_2": "Generate a motivational, mentor-style affirmation that inspires someone learning, failing, and growing in tech. Max 20 words.",
    "affirmation_3": "Give a daily positive affirmation for someone overcoming self-doubt while learning to code. Warm and hopeful tone. Keeping it under to short paragraph.",
    "intro": "Write a warm and confident intro message from {name} who wants to {goal} and {fun}.",
    "coach": "Rephrase this with empathy and clarity: '{question}'",
    "ask": "Give a helpful, kind response to this anonymous mentee question: '{question}'"
}

# Gemini Query Function
async def query_gemini(prompt: str) -> str:
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    print("📤 Gemini Prompt:", prompt)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            print("✅ Gemini Response:", result)
            return result["candidates"][0]["content"]["parts"][0]["text"]

    except (HTTPError, TimeoutException) as e:
        print("❌ Gemini HTTP error:", str(e))
        return "There was a problem connecting to Gemini."

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        print(traceback.format_exc())
        return "An internal error occurred while processing your request."

# Root check
@app.get("/")
def home():
    return {"message": "MentorBridge Gemini backend is live 🎯"}

# ✅ Fixed: No JSON body required
@app.post("/affirmation")
async def affirmation():
    prompt = random.choice([
        TEMPLATES["affirmation_1"],
        TEMPLATES["affirmation_2"],
        TEMPLATES["affirmation_3"]
    ])
    reply = await query_gemini(prompt)
    return {"reply": reply}

@app.post("/intro-message")
async def intro_message(req: Request):
    try:
        data = await req.json()
        prompt = TEMPLATES["intro"].format(
            name=data.get("name", "a mentee"),
            goal=data.get("goal", "learn Flutter"),
            fun=data.get("fun", "enjoys anime")
        )
    except JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format. Expected application/json body."})
    except (ValueError, KeyError, TypeError) as e:
        return JSONResponse(status_code=422, content={"error": f"Data error: {str(e)}"})

    reply = await query_gemini(prompt)
    return {"reply": reply}

@app.post("/coach")
async def coach(req: Request):
    try:
        data = await req.json()
        question = data.get("question")
        if not question:
            return JSONResponse(status_code=422, content={"error": "Missing 'question' field."})
        prompt = TEMPLATES["coach"].format(question=question)
    except JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format."})
    except (ValueError, KeyError, TypeError) as e:
        return JSONResponse(status_code=422, content={"error": f"Data error: {str(e)}"})

    reply = await query_gemini(prompt)
    return {"reply": reply}

@app.post("/ask-reply")
async def ask_reply(req: Request):
    try:
        data = await req.json()
        question = data.get("question")
        if not question:
            return JSONResponse(status_code=422, content={"error": "Missing 'question' field."})
        prompt = TEMPLATES["ask"].format(question=question)
    except JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format."})
    except (ValueError, KeyError, TypeError) as e:
        return JSONResponse(status_code=422, content={"error": f"Data error: {str(e)}"})

    reply = await query_gemini(prompt)
    return {"reply": reply}

@app.post("/celebrate")
async def celebrate_win(req: Request):
    data = await req.json()
    achievement = data.get("achievement", "")
    prompt = f"Write a short, energetic, and inspiring celebration message for someone who achieved this: {achievement}"
    reply = await query_gemini(prompt)
    return {"reply": reply}
