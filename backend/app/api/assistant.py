import logging

from fastapi import APIRouter, HTTPException
from typing import Literal

from pydantic import BaseModel, Field

from app.rag.schemas import RAGAnswer
from app.rag.service import answer_question


logger = logging.getLogger(__name__)

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
    role: Literal[
        "bank_employee",
        "compliance_officer",
        "branch_manager",
        "customer_support",
    ] = "bank_employee"


@router.post("/query", response_model=RAGAnswer)
def query_assistant(request: AssistantQueryRequest) -> RAGAnswer:
    try:
        if request.role == "bank_employee":
            return answer_question(
                question=request.question,
                top_k=request.top_k,
            )
        return answer_question(
            question=request.question,
            top_k=request.top_k,
            role=request.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected failure in assistant query endpoint")
        raise HTTPException(
            status_code=500,
            detail="Unable to process the compliance question.",
        ) from exc
