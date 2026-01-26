import asyncio

from fastapi import FastAPI
from services.api_kudago import print_url

app = FastAPI()

@app.get("/")
def index():
    return {"result": print_url()}

    
