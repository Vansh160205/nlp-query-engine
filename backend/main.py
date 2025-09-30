from fastapi import FastAPI
from api.routes import ingestion
from api.routes import query as query_router
# Example for a FastAPI backend
from fastapi.middleware.cors import CORSMiddleware


from dotenv import load_dotenv
load_dotenv()
app = FastAPI(
    title="NLP Query Engine API",
    description="API for database schema discovery, document ingestion, and natural language querying.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow your React app's origin
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

# Include the ingestion router
app.include_router(ingestion.router, prefix="/api", tags=["Data Ingestion"])
app.include_router(query_router.router, prefix="/api", tags=["query"])

@app.get("/")
async def root():
    return {"message": "AI Query Engine Backend is running!"}

# In a real app, you might have more routers for querying, etc.
# app.include_router(query.router, prefix="/api", tags=["Query"])
