from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List

from services.schema_discovery import SchemaDiscovery

from api.routes.query import qe

router = APIRouter()

@router.post("/connect-database")
async def connect_database(connection_string: str = Form(...)):
    """
    Connects to a database using the provided connection string and
    discovers its schema.
    """
    print(f"Connecting to DB with connection string: {connection_string}")
    qe.connect_db(connection_string=connection_string)  # <-- set schema and DB engine

    discovery_service = SchemaDiscovery()
    schema = discovery_service.analyze_database(connection_string)
    
    if "error" in schema:
        raise HTTPException(status_code=400, detail=schema["error"])
        
    return {"message": "Database schema discovered successfully", "schema": schema}

@router.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    file_contents = []
    for file in files:
        content = await file.read()
        file_contents.append({"filename": file.filename, "content": content})

    # Call the process_documents method on the processor inside our shared qe instance
    result = qe.doc_processor.process_documents(file_contents)
    
    print("Vector index total after upload:", qe.doc_processor.vector_index.ntotal)
    return result