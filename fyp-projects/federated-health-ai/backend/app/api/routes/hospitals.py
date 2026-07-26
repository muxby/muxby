from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import (
    HospitalCreate,
    HospitalDetail,
    HospitalMetric,
    HospitalOut,
    HospitalUpdate,
)
from app.services import hospital_service
from app.services.hospital_service import HospitalNameTaken, HospitalNotFound

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("", response_model=list[HospitalOut])
def list_hospitals(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return hospital_service.list_hospitals(db)


@router.post("", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
def create_hospital(
    payload: HospitalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return hospital_service.create_hospital(db, payload, user.email)
    except HospitalNameTaken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hospital name already exists")


@router.get("/{hospital_id}", response_model=HospitalDetail)
def get_hospital(hospital_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        hospital = hospital_service.get_hospital(db, hospital_id)
        metrics = hospital_service.hospital_metrics(db, hospital_id)
    except HospitalNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    detail = HospitalDetail.model_validate(hospital)
    detail.metrics = [HospitalMetric(**m) for m in metrics]
    return detail


@router.patch("/{hospital_id}", response_model=HospitalOut)
def update_hospital(
    hospital_id: int,
    payload: HospitalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return hospital_service.update_hospital(db, hospital_id, payload, user.email)
    except HospitalNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    except HospitalNameTaken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hospital name already exists")


@router.delete("/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        hospital_service.delete_hospital(db, hospital_id, user.email)
    except HospitalNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
