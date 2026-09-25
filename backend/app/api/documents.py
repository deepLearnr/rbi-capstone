from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.document_chunk import (
    DocumentChunkCreate,
    DocumentChunkResponse,
)

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.get("/", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return db.scalars(
        select(Document).order_by(Document.id)
    ).all()


@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
):
    new_document = Document(
        **document.model_dump(mode="json")
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkResponse],
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()


@router.post(
    "/{document_id}/chunks",
    response_model=DocumentChunkResponse,
)
def create_document_chunk(
    document_id: int,
    chunk: DocumentChunkCreate,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    #Turn the chunk schema data into a dictionary
    chunk_data = chunk.model_dump()
    
    #Safely map 'metadata' payload to the 'chunk_metadata' database attribute name
    payload_metadata = chunk_data.pop("metadata", None)

    new_chunk = DocumentChunk(
        document_id=document_id,
        chunk_metadata=payload_metadata,  # Explicit mapping to match our warning-fix
        **chunk_data,
    )

    db.add(new_chunk)
    db.commit()
    db.refresh(new_chunk)

    return new_chunk
