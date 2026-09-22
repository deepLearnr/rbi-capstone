from fastapi import APIRouter
from app.schemas.circular import CircularCreate, CircularResponse

router = APIRouter(
    prefix="/api/circulars",
    tags=["Circulars"],
)


# Temporary in-memory storage.
# We'll replace this with PostgreSQL later.
circulars: list[CircularResponse] = []


@router.get("/", response_model=list[CircularResponse])
def get_circulars():
    return circulars


@router.post("/", response_model=CircularResponse)
def create_circular(circular: CircularCreate):
    new_circular = CircularResponse(
        id=len(circulars) + 1,
        **circular.model_dump(),
    )

    circulars.append(new_circular)

    return new_circular