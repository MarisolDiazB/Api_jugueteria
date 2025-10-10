from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_db
from apis.models import Discount
from apis.schemas import DiscountIn, DiscountOut, DiscountUpdate
from apis.routers.auth import get_current_user

router = APIRouter = APIRouter (prefix="/discounts", tags=["Descuentos"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[DiscountOut])
def list_discounts(q: str | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Discount)
    if q:
        query = query.filter(func.lower(Discount.name).like(f"%{q.lower()}%"))
    return query.order_by(Discount.name).all()

@router.get("/{discount_id}", response_model=DiscountOut)
def get_discount(discount_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Discount, discount_id)
    if not obj:
        raise HTTPException(404, "Descuento no encontrado")
    return obj

@router.post("/", response_model=DiscountOut, status_code=status.HTTP_201_CREATED)
def create_discount(payload: DiscountIn, db: Session = Depends(get_db)):
    if db.query(Discount).filter(func.lower(Discount.name) == payload.name.lower()).first():
        raise HTTPException(409, "Ya existe un descuento con ese nombre")
    obj = Discount(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{discount_id}", response_model=DiscountOut)
def update_discount(discount_id: UUID, payload: DiscountIn, db: Session = Depends(get_db)):
    obj = db.get(Discount, discount_id)
    if not obj:
        raise HTTPException(404, "Descuento no encontrado")
    conflict = db.query(Discount).filter(
        func.lower(Discount.name) == payload.name.lower(), Discount.id != discount_id
    ).first()
    if conflict:
        raise HTTPException(409, "Otro descuento ya usa ese nombre")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{discount_id}", response_model=DiscountOut)
def patch_discount(discount_id: UUID, payload: DiscountUpdate, db: Session = Depends(get_db)):
    obj = db.get(Discount, discount_id)
    if not obj:
        raise HTTPException(404, "Descuento no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        conflict = db.query(Discount).filter(
            func.lower(Discount.name) == data["name"].lower(), Discount.id != discount_id
        ).first()
        if conflict: raise HTTPException(409, "Otro descuento ya usa ese nombre")
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discount(discount_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Discount, discount_id)
    if not obj: raise HTTPException(404, "Descuento no encontrado")
    db.delete(obj); db.commit()
