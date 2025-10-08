from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database.connection import get_db
from apis.models import Customer
from apis.schemas import CustomerIn, CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["Clientes"])


@router.get("", response_model=List[CustomerOut])
def list_customers(
    q: Optional[str] = Query(None, description="Buscar por nombre o email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Customer)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            func.lower(Customer.name).like(like) | func.lower(Customer.email).like(like)
        )
    stmt = stmt.order_by(Customer.fecha_creacion.desc()).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay clientes")
    return rows


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    entity = db.get(Customer, customer_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return entity


@router.get("/filter/by-email", response_model=List[CustomerOut])
def filter_by_email(email: str = Query(...), db: Session = Depends(get_db)):
    stmt = select(Customer).where(func.lower(Customer.email) == email.lower())
    rows = db.execute(stmt).scalars().all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron clientes con ese correo")
    return rows


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db)):
   
    exists = db.execute(
        select(func.count()).select_from(Customer).where(func.lower(Customer.email) == payload.email.lower())
    ).scalar_one()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    entity = Customer(**payload.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: UUID, payload: CustomerUpdate, db: Session = Depends(get_db)):
    entity = db.get(Customer, customer_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    if payload.email.lower() != entity.email.lower():
        exists = db.execute(
            select(func.count()).select_from(Customer).where(func.lower(Customer.email) == payload.email.lower())
        ).scalar_one()
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    for k, v in payload.model_dump().items():
        setattr(entity, k, v)

    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: UUID, db: Session = Depends(get_db)):
    entity = db.get(Customer, customer_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    db.delete(entity)
    db.commit()
