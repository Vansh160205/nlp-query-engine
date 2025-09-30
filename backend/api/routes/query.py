# backend/routes/query.py
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional

from services.query_engine import QueryEngine

router = APIRouter()

# Create a single engine instance (could be injected)
# For demo, you can pass None and call engine.connect_db later via /connect-database route
qe = QueryEngine()

class QueryRequest(BaseModel):
    query: str
    top_k_docs: Optional[int] = 5
    schema_hash: Optional[str] = ""


@router.post("/query")
async def process_query(body: QueryRequest):
    """
    Process a natural language query. Returns SQL results, document matches, and metrics.
    """
    if not body.query or not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must be provided.")

    if not qe.schema or "tables" not in qe.schema:
        raise HTTPException(status_code=400, detail="Database not connected. Call /connect-database first.")

    result = qe.process_query(body.query, top_k_docs=body.top_k_docs, schema_hash=body.schema_hash or "")
    return result


@router.get("/query/history")
async def query_history(limit: int = 50):
    return {"history": qe.get_history(limit)}


