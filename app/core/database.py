# app/core/database.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["mentorbridge"]

# Collections
users_collection = db["users"]
mentors_collection = db["mentors"]
mentees_collection = db["mentees"]