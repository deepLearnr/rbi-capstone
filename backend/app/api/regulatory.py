from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.regulatory_update import RegulatoryUpdate
from app.schemas.regulatory import RegulatoryUpdateResponse


router = APIRouter(
    prefix="/api/regulatory",
    tags=["Regulatory Updates"],
)


@router.get(
    "/updates",
    response_model=list[RegulatoryUpdateResponse],
)
def get_regulatory_updates(
    db: Session = Depends(get_db),
):
    return (
        db.query(RegulatoryUpdate)
        .order_by(
            RegulatoryUpdate.publication_date.desc(),
            RegulatoryUpdate.id.desc(),
        )
        .all()
    )


@router.get(
    "/updates/{update_id}",
    response_model=RegulatoryUpdateResponse,
)
def get_regulatory_update(
    update_id: int,
    db: Session = Depends(get_db),
):
    update = (
        db.query(RegulatoryUpdate)
        .filter(RegulatoryUpdate.id == update_id)
        .one_or_none()
    )

    if update is None:
        raise HTTPException(
            status_code=404,
            detail="Regulatory update not found.",
        )

    return update
