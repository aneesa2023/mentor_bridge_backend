# from fastapi import FastAPI
# from app.api.routes import users

# app = FastAPI()

# app.include_router(users.router)

from fastapi import FastAPI
from app.api.routes import public, private
from mangum import Mangum
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()

# Mount routers
app.include_router(public.router)
app.include_router(private.router)

# Required for Lambda
def handler(event, context):
    lambda_handler = Mangum(app)
    return lambda_handler(event, context)




