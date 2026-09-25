from fastapi import FastAPI

from app.api.circulars import router as circular_router
from app.api.documents import router as document_router

app = FastAPI(
    title="GenAI Capstone API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "genai-capstone-backend",
    }


app.include_router(circular_router)
app.include_router(document_router)