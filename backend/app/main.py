from fastapi import FastAPI

from app.api.circulars import router as circular_router


app = FastAPI(
    title="RBI Saathi API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "rbi-saathi-backend",
    }


app.include_router(circular_router)