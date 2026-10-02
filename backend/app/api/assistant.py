from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.schemas import RAGAnswer
from app.rag.service import answer_question


router = APIRouter(
    prefix="/api/assistant",
    tags=["assistant"],
)


class AssistantQueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


@router.post("/query", response_model=RAGAnswer)
def query_assistant(request: AssistantQueryRequest) -> RAGAnswer:
    try:
        return answer_question(
            question=request.question,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the compliance question.",
        ) from exc
