from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

from agent.agent import query

app = FastAPI(title="VaR Risk Agent", version="1.0.0")
security = HTTPBearer()

API_KEY = os.getenv("AGENT_API_KEY", "dev-key-change-me")


def verify_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


class QueryRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest, _: str = Depends(verify_key)):
    answer = query(request.message)
    return QueryResponse(answer=answer)
