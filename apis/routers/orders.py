from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from apis.models import Order, Customer, Discount
from apis.schemas import OrderIn, OrderOut, OrderUpdate
from apis.routers.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Órdenes"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.fecha_creacion.desc()).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Order, order_id)
    if not obj: raise HTTPException(404, "Orden no encontrada")
    return obj

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    if not db.get(Customer, payload.customer_id):
        raise HTTPException(400, "customer_id inválido")
    if payload.discount_id and not db.get(Discount, payload.discount_id):
        raise HTTPException(400, "discount_id inválido")
    obj = Order(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: UUID, payload: OrderIn, db: Session = Depends(get_db)):
    obj = db.get(Order, order_id)
    if not obj: raise HTTPException(404, "Orden no encontrada")
    if not db.get(Customer, payload.customer_id):
        raise HTTPException(400, "customer_id inválido")
    if payload.discount_id and not db.get(Discount, payload.discount_id):
        raise HTTPException(400, "discount_id inválido")
    for k, v in payload.model_dump().items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.patch("/{order_id}", response_model=OrderOut)
def patch_order(order_id: UUID, payload: OrderUpdate, db: Session = Depends(get_db)):
    obj = db.get(Order, order_id)
    if not obj: raise HTTPException(404, "Orden no encontrada")
    data = payload.model_dump(exclude_unset=True)
    if "customer_id" in data and data["customer_id"] and not db.get(Customer, data["customer_id"]):
        raise HTTPException(400, "customer_id inválido")
    if "discount_id" in data and data["discount_id"] and not db.get(Discount, data["discount_id"]):
        raise HTTPException(400, "discount_id inválido")
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Order, order_id)
    if not obj: raise HTTPException(404, "Orden no encontrada")
    db.delete(obj); db.commit()
