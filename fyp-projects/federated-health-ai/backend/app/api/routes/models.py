from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import ModelVersionOut
from app.services import model_service
from app.services.model_service import ModelNotFound

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelVersionOut])
def list_models(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return model_service.list_models(db)


@router.get("/{model_id}", response_model=ModelVersionOut)
def get_model(model_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        return model_service.get_model(db, model_id)
    except ModelNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")


@router.post("/{model_id}/activate", response_model=ModelVersionOut)
def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return model_service.activate_model(db, model_id, user.email)
    except ModelNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
