import os
import asyncio
from pymongo import MongoClient
import google.generativeai as genai
import logging
import numpy as np
from bson.objectid import ObjectId

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# Constants
MAX_MENTORS = 30
TOP_MATCHES = 10

# Helper to sanitize mentor data
def sanitize_mentor(mentor):
    mentor = dict(mentor)
    mentor.pop("email", None)
    mentor.pop("phone", None)
    mentor["_id"] = str(mentor.get("_id"))
    return mentor

# Helper to calculate vector similarity
def calculate_vector_similarity(vector1, vector2):
    if not vector1 or not vector2:
        return 0
    
    # Convert lists of dicts to numpy arrays
    if isinstance(vector1[0], dict):
        vector1 = [float(v.get("$numberDouble", 0)) for v in vector1]
    if isinstance(vector2[0], dict):
        vector2 = [float(v.get("$numberDouble", 0)) for v in vector2]
    
    # Ensure vectors are the same length
    min_length = min(len(vector1), len(vector2))
    vector1 = vector1[:min_length]
    vector2 = vector2[:min_length]
    
    # Calculate cosine similarity
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = sum(a * a for a in vector1) ** 0.5
    magnitude2 = sum(b * b for b in vector2) ** 0.5
    
    if magnitude1 * magnitude2 == 0:
        return 0
    
    return dot_product / (magnitude1 * magnitude2)

# Calculate initial compatibility score based on profile data
def calculate_initial_score(mentee, mentor):
    score = 0
    
    # Language match (up to 15 points)
    common_languages = set(mentee.get("languages_spoken", [])).intersection(mentor.get("languages_spoken", []))
    score += min(len(common_languages) * 5, 15)
    
    # Industry match (up to 15 points)
    mentee_industries = mentee.get("industries_interested", [])
    mentor_industries = mentor.get("industries", [])
    common_industries = set(mentee_industries).intersection(mentor_industries)
    score += min(len(common_industries) * 5, 15)
    
    # Domain match (up to 15 points)
    mentee_domains = mentee.get("domains_interested", [])
    mentor_domains = mentor.get("domains", [])
    common_domains = set(mentee_domains).intersection(mentor_domains)
    score += min(len(common_domains) * 5, 15)
    
    # Tech stack match (up to 15 points)
    mentee_tech = mentee.get("tech_stack_interest", [])
    mentor_tech = mentor.get("tech_stack", [])
    common_tech = set(mentee_tech).intersection(mentor_tech)
    score += min(len(common_tech) * 3, 15)
    
    # Mentee type match (10 points)
    mentee_tags = set(mentee.get("mentee_tags", []))
    mentor_preferred_types = set(mentor.get("mentee_types_to_help", []))
    if mentee_tags.intersection(mentor_preferred_types):
        score += 10
    
    # Vector similarity (up to 20 points)
    vector_similarity = calculate_vector_similarity(
        mentee.get("profile_vector", []),
        mentor.get("profile_vector", [])
    )
    score += int(vector_similarity * 20)
    
    # Availability (10 points if mentor has any availability)
    if mentor.get("availability") and any(mentor["availability"].values()):
        score += 10
    
    return score

# Gemini prompt
def build_prompt(mentee, mentor, initial_score):
    return f"""
You are an AI mentor matching assistant that evaluates mentor-mentee compatibility.

Match this mentee with this mentor and provide a compatibility score from 0 to 100 and 2-3 specific reasons why they would work well together.

Mentee Profile:
- Name: {mentee.get("full_name")}
- School: {mentee.get("school")}
- Languages: {", ".join(mentee.get("languages_spoken", []))}
- Industries Interested: {", ".join(mentee.get("industries_interested", []))}
- Domains Interested: {", ".join(mentee.get("domains_interested", []))}
- Tech Stack Interest: {", ".join(mentee.get("tech_stack_interest", []))}
- Experience Background: {mentee.get("experience_background")}
- Education Level: {mentee.get("education_level")}
- Goals: {", ".join(mentee.get("goals", []))}
- Mentee Tags: {", ".join(mentee.get("mentee_tags", []))}
- Fun Facts: {mentee.get("fun_facts")}
- AI Summary: {mentee.get("ai_summary")}

Mentor Profile:
- Name: {mentor.get("full_name")}
- Current Role: {mentor.get("current_company_role")}
- Experience: {mentor.get("experience_years")} years
- Languages: {", ".join(mentor.get("languages_spoken", []))}
- Industries: {", ".join(mentor.get("industries", []))}
- Domains: {", ".join(mentor.get("domains", []))}
- Tech Stack: {", ".join(mentor.get("tech_stack", []))}
- Education Level: {mentor.get("education_level")}
- Mentoring Style: {", ".join(mentor.get("mentoring_style", []))}
- Personality Tags: {", ".join(mentor.get("personality_tags", []))}
- Communication Style: {", ".join(mentor.get("communication_style", []))}
- Mentee Types to Help: {", ".join(mentor.get("mentee_types_to_help", []))}
- Mentoring Reason: {mentor.get("mentoring_reason")}
- Past Roles: {", ".join(mentor.get("past_roles", []))}
- AI Summary: {mentor.get("ai_summary")}

Initial compatibility score based on profile matching: {initial_score}/100

Based on the profiles above and the initial compatibility score, provide your final compatibility score and specific reasons why they would be a good match. Focus especially on:
1. Alignment of the mentee's goals with mentor's expertise
2. Compatibility of personality and communication styles
3. Relevant experience the mentor has to address the mentee's specific needs

Respond in this format:
Score: <0-100>
Reasons:
- <reason 1>
- <reason 2>
- <reason 3>
"""

# Gemini scoring logic
async def score_mentor(mentee, mentor):
    try:
        initial_score = calculate_initial_score(mentee, mentor)
        prompt = build_prompt(mentee, mentor, initial_score)
        response = await model.generate_content_async(prompt)
        text = response.text.strip()

        # Default to initial score if parsing fails
        score = initial_score
        reasons = []
        
        if "Score:" in text:
            score_line = text.split("Score:")[1].splitlines()[0]
            try:
                score = int(''.join(filter(str.isdigit, score_line)))
            except ValueError:
                logging.warning(f"Could not parse score from: {score_line}")
        
        if "Reasons:" in text:
            reasons_section = text.split("Reasons:")[1]
            reasons = [r.strip("-• ") for r in reasons_section.strip().splitlines() if r.strip()]

        return {
            "mentor": sanitize_mentor(mentor),
            "score": score,
            "initial_score": initial_score,
            "reasons": reasons
        }

    except Exception as e:
        logging.exception(f"Error scoring mentor {mentor.get('_id')}")
        initial_score = calculate_initial_score(mentee, mentor)
        return {
            "mentor": sanitize_mentor(mentor),
            "score": initial_score,
            "initial_score": initial_score,
            "reasons": ["Could not evaluate with AI due to error. Score based on profile matching only."]
        }

# MAIN lambda handler
async def lambda_handler(event, context):
    try:
        mentee_id = event.get("mentee_id")
        if isinstance(mentee_id, str):
            mentee_id = ObjectId(mentee_id)
        
        # MongoDB Connection
        client = MongoClient(os.environ["MONGO_URI"])
        db = client[os.environ["DB_NAME"]]

        # Get Mentee
        mentee = db.mentees.find_one({"_id": mentee_id})
        if not mentee:
            return {"error": "Mentee not found", "mentee_id": str(mentee_id)}

        # Get all Mentors
        query = {}
        
        # Apply basic filters if specified in the event
        if event.get("filters"):
            filters = event.get("filters")
            
            if filters.get("industries"):
                query["industries"] = {"$in": filters["industries"]}
                
            if filters.get("domains"):
                query["domains"] = {"$in": filters["domains"]}
                
            if filters.get("tech_stack"):
                query["tech_stack"] = {"$in": filters["tech_stack"]}
                
            if filters.get("experience_min"):
                query["experience_years"] = {"$gte": filters["experience_min"]}
        
        all_mentors = list(db.mentors.find(query))
        logging.info(f"Found {len(all_mentors)} mentors matching initial filters")
        
        # Prefilter mentors based on basic compatibility
        filtered_mentors = []
        for mentor in all_mentors:
            # Check for any overlap in languages
            if not set(mentee.get("languages_spoken", [])).intersection(mentor.get("languages_spoken", [])):
                continue
                
            # Check for any overlap in industries or domains
            if not (set(mentee.get("industries_interested", [])).intersection(mentor.get("industries", [])) or 
                   set(mentee.get("domains_interested", [])).intersection(mentor.get("domains", []))):
                continue
                
            # Add mentor to filtered list
            filtered_mentors.append(mentor)
            
            # Stop if we have enough mentors
            if len(filtered_mentors) >= MAX_MENTORS:
                break
        
        logging.info(f"Filtered to {len(filtered_mentors)} potential mentors for detailed evaluation")
        
        # If we have no mentors after filtering, return empty results
        if not filtered_mentors:
            return {
                "mentee_id": str(mentee_id),
                "top_matches": []
            }

        # Score matches with Gemini
        tasks = [score_mentor(mentee, m) for m in filtered_mentors]
        results = await asyncio.gather(*tasks)

        # Sort by score and return top N
        top_matches = sorted(results, key=lambda x: x["score"], reverse=True)[:TOP_MATCHES]

        return {
            "mentee_id": str(mentee_id),
            "top_matches": top_matches
        }
        
    except Exception as e:
        logging.exception("Error in lambda_handler")
        return {
            "error": str(e),
            "mentee_id": str(event.get("mentee_id", "unknown"))
        }

    
# zip function.zip get_filtered_mentors_lambda.py
# aws lambda update-function-code \
#     --function-name MBFilterMentorsLambda \
#     --zip-file fileb://function.zip \
#     --region us-east-1