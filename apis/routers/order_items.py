from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from apis.models import OrderItem, Order, Product
from apis.schemas import OrderItemIn, OrderItemOut, OrderItemUpdate
from apis.routers.auth import get_current_user

router = APIRouter(prefix="/order_items", tags=["Items de Orden"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[OrderItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(OrderItem).order_by(OrderItem.fecha_creacion.desc()).all()

@router.get("/{item_id}", response_model=OrderItemOut)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    return obj

@router.post("/", response_model=OrderItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: OrderItemIn, db: Session = Depends(get_db)):
    if not db.get(Order, payload.order_id):
        raise HTTPException(400, "order_id inválido")
    if not db.get(Product, payload.product_id):
        raise HTTPException(400, "product_id inválido")
    obj = OrderItem(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{item_id}", response_model=OrderItemOut)
def update_item(item_id: UUID, payload: OrderItemIn, db: Session = Depends(get_db)):
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    if not db.get(Order, payload.order_id):
        raise HTTPException(400, "order_id inválido")
    if not db.get(Product, payload.product_id):
        raise HTTPException(400, "product_id inválido")
    for k, v in payload.model_dump().items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.patch("/{item_id}", response_model=OrderItemOut)
def patch_item(item_id: UUID, payload: OrderItemUpdate, db: Session = Depends(get_db)):
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    db.delete(obj); db.commit()
