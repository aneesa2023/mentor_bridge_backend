from fastapi import FastAPI, Request
import os, logging, httpx

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

TEMPLATE = """Based on the following mentor profile, write a professional and inspiring summary in 4-5 lines suitable for a mentorship platform. Use an inviting, clear tone:
Name: {full_name}
Current Role: {current_company_role}
Experience: {experience_years} years
Industries: {industries}
Domains: {domains}
Tech Stack: {tech_stack}
Mentoring Style: {mentoring_style}
Personality: {personality_tags}
Reason to mentor: {mentoring_reason}"""

@app.post("/gemini-summary")
async def mentor_summary(req: Request):
    data = await req.json()
    prompt = TEMPLATE.format(
        full_name=data.get("full_name", ""),
        current_company_role=data.get("current_company_role", ""),
        experience_years=data.get("experience_years", ""),
        industries=", ".join(data.get("industries", [])),
        domains=", ".join(data.get("domains", [])),
        tech_stack=", ".join(data.get("tech_stack", [])),
        mentoring_style=", ".join(data.get("mentoring_style", [])),
        personality_tags=", ".join(data.get("personality_tags", [])),
        mentoring_reason=data.get("mentoring_reason", "")
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(GEMINI_URL, json=payload)
            result = response.json()
            return {"reply": result["candidates"][0]["content"]["parts"][0]["text"]}
    except Exception as e:
        logging.error("Summary error: %s", e)
        return {"reply": "Error generating mentor summary"}
