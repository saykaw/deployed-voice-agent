# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from dispatch import create_explicit_dispatch

app = FastAPI()

class DispatchRequest(BaseModel):
    customer_phone: str

@app.post("/dispatch")
async def create_dispatch(request: DispatchRequest):
    try:
        result = await create_explicit_dispatch(request.customer_phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
