from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import random
import requests
import logging
import traceback
from jose import jwt
from dotenv import load_dotenv
from json.decoder import JSONDecodeError
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your Flutter web/mobile origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
API_IDENTIFIER = os.getenv("AUTH0_API_IDENTIFIER")
ALGORITHMS = [os.getenv("AUTH0_ALGORITHMS")]

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Prompt Templates
TEMPLATES = {
    "affirmation_1": "Write a short, calming affirmation for someone building confidence in their tech journey. Keep it under 20 words.",
    "affirmation_2": "Generate a motivational, mentor-style affirmation that inspires someone learning, failing, and growing in tech. Max 20 words.",
    "affirmation_3": "Give a daily positive affirmation for someone overcoming self-doubt while learning to code. Warm and hopeful tone.",
    "intro": "Write a warm and confident intro message from {name} who wants to {goal} and {fun}.",
    "coach": "Rephrase this with empathy and clarity: '{question}'",
    "ask": "Give a helpful, kind response to this anonymous mentee question: '{question}'"
}

# Root route
@app.get("/")
def home():
    return {"message": "MentorBridge Gemini backend is live 🎯"}

# JWKS fetcher for token validation
def get_jwks():
    try:
        return requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").json()
    except Exception as e:
        logging.error("Failed to fetch JWKS: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch JWKS")

# Auth0 User Init
@app.post("/api/users/init")
async def init_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next(key for key in jwks["keys"] if key["kid"] == unverified_header["kid"])

        payload = jwt.decode(
            token,
            key=rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_CLIENT_ID,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )

        user_id = payload["sub"]
        email = payload.get("email")

        return {"user_id": user_id, "email": email}

    except Exception as e:
        logging.error("Token verification failed: %s", traceback.format_exc())
        raise HTTPException(status_code=401, detail="Invalid token")

# Gemini Query Function
async def query_gemini(prompt: str) -> str:
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    logging.info("Prompt sent to Gemini: %s", prompt)
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logging.error("Gemini HTTP error: %s", e)
        return "There was a problem connecting to Gemini."
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        logging.error(traceback.format_exc())
        return "An internal error occurred while processing your request."

# Affirmation endpoint
@app.post("/affirmation")
async def affirmation():
    try:
        prompt = random.choice([
            TEMPLATES["affirmation_1"],
            TEMPLATES["affirmation_2"],
            TEMPLATES["affirmation_3"]
        ])
        reply = await query_gemini(prompt)
        return {"reply": reply}
    except Exception as e:
        logging.error("Affirmation error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error generating affirmation")

# Intro message
@app.post("/intro-message")
async def intro_message(req: Request):
    try:
        data = await req.json()
        prompt = TEMPLATES["intro"].format(
            name=data.get("name", "a mentee"),
            goal=data.get("goal", "learn Flutter"),
            fun=data.get("fun", "enjoys anime")
        )
        reply = await query_gemini(prompt)
        return {"reply": reply}
    except JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format."})
    except Exception as e:
        logging.error("Intro message error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error generating intro message")

# Conversation coach
@app.post("/coach")
async def coach(req: Request):
    try:
        data = await req.json()
        question = data.get("question")
        if not question:
            return JSONResponse(status_code=422, content={"error": "Missing 'question' field."})
        prompt = TEMPLATES["coach"].format(question=question)
        reply = await query_gemini(prompt)
        return {"reply": reply}
    except JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format."})
    except Exception as e:
        logging.error("Coach error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error processing coach message")

# Ask reply
@app.post("/ask-reply")
async def ask_reply(req: Request):
    try:
        data = await req.json()
        question = data.get("question")
        if not question:
            return JSONResponse(status_code=422, content={"error": "Missing 'question' field."})
        prompt = TEMPLATES["ask"].format(question=question)
        reply = await query_gemini(prompt)
        return {"reply": reply}
    except JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format."})
    except Exception as e:
        logging.error("Ask reply error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error generating ask reply")

# Celebration win
@app.post("/celebrate")
async def celebrate_win(req: Request):
    try:
        data = await req.json()
        achievement = data.get("achievement", "")
        prompt = f"Write a short, energetic, and inspiring celebration message for someone who achieved this: {achievement}"
        reply = await query_gemini(prompt)
        return {"reply": reply}
    except Exception as e:
        logging.error("Celebrate win error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error generating celebration message")
