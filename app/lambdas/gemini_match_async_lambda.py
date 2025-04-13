import os
import asyncio
# import google.generativeai as genai
from google import genai
import logging

# Configure Gemini API
genai.configure(api_key=os.environ["gemini-key"])
model = genai.GenerativeModel("gemini-pro")

# Optional: Cap the number of mentors to avoid timeouts
MAX_MENTORS = 30
TOP_MATCHES = 10

# Build a personalized prompt for each mentor
def build_prompt(mentee, mentor):
    return f"""
You are an AI mentor matching assistant.

Match this mentee with this mentor and provide a compatibility score from 0 to 100 and 2-3 reasons why they would work well together.

Mentee Profile:
- Name: {mentee.get("full_name")}
- Languages: {", ".join(mentee.get("languages_spoken", []))}
- Interests: {", ".join(mentee.get("areas_of_interest", []))}
- Preferred Communication: {", ".join(mentee.get("communication_style", []))}
- Goals: {", ".join(mentee.get("mentee_looking_for", []))}
- Personality: {", ".join(mentee.get("personality_tags", []))}

Mentor Profile:
- Name: {mentor.get("full_name")}
- Experience: {mentor.get("experience_years")} years
- Languages: {", ".join(mentor.get("languages_spoken", []))}
- Interests: {", ".join(mentor.get("areas_of_interest", []))}
- Mentoring Style: {", ".join(mentor.get("mentoring_style", []))}
- Personality: {", ".join(mentor.get("personality_tags", []))}
- Communication: {", ".join(mentor.get("communication_style", []))}

Respond in this format:
Score: <0-100>
Reasons: <bullet points>
"""

# Async function to send a prompt to Gemini and parse response
async def score_mentor(mentee, mentor):
    try:
        prompt = build_prompt(mentee, mentor)
        response = await model.generate_content_async(prompt)
        text = response.text.strip()

        score = 0
        reasons = []
        if "Score:" in text:
            score_line = text.split("Score:")[1].splitlines()[0]
            score = int(''.join(filter(str.isdigit, score_line)))
        if "Reasons:" in text:
            reasons_section = text.split("Reasons:")[1]
            reasons = [r.strip("-• ") for r in reasons_section.strip().splitlines() if r.strip()]

        return {
            "mentor_id": str(mentor.get("_id")),
            "score": score,
            "reasons": reasons
        }

    except Exception as e:
        logging.exception(f"Error scoring mentor {mentor.get('_id')}")
        return {
            "mentor_id": str(mentor.get("_id")),
            "score": 0,
            "reasons": ["Could not evaluate due to error."]
        }

# Lambda handler
async def lambda_handler(event, context):
    mentee = event["mentee"]
    mentors = event.get("mentors", [])[:MAX_MENTORS]

    tasks = [score_mentor(mentee, m) for m in mentors]
    results = await asyncio.gather(*tasks)

    # Sort by score
    top_matches = sorted(results, key=lambda x: x["score"], reverse=True)[:TOP_MATCHES]

    return {
        "mentee_id": str(mentee.get("_id")),
        "top_matches": top_matches
    }
    
# zip function.zip get_filtered_mentors_lambda.py
# aws lambda update-function-code \
#     --function-name MBGeminiMatching \
#     --zip-file fileb://function.zip \
#     --region us-east-1