import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "python"))

from fastapi import FastAPI
from mangum import Mangum
from app.api.routes import public

app = FastAPI()
app.include_router(public.router)

handler = Mangum(app)