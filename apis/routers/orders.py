from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date
from models import Order, OrderItem
from db import orders_db, order_items_db

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# Obtener todos los pedidos
@router.get("", response_model=List[Order])
def get_all_orders():
    return orders_db

# Obtener pedido por id
@router.get("/{order_id}", response_model=Order)
def get_order_by_id(order_id: int):
    for order in orders_db:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order no encontrado")

# Crear un pedido
@router.post("", response_model=Order, status_code=201)
def create_order(order: Order):
    # Validar ID único
    for o in orders_db:
        if o.id == order.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
    orders_db.append(order)
    return order

# Actualizar un pedido
@router.put("/{order_id}", response_model=Order)
def update_order(order_id: int, update_order: Order):
    for index, o in enumerate(orders_db):
        if o.id == order_id:
            # 🔒 No cambiar ID
            if update_order.id != order_id:
                raise HTTPException(status_code=400, detail="No se puede modificar el ID")
            orders_db[index] = update_order
            return update_order
    raise HTTPException(status_code=404, detail="Order no encontrado")

# Eliminar un pedido
@router.delete("/{order_id}")
def delete_order(order_id: int):
    for index, o in enumerate(orders_db):
        if o.id == order_id:
            orders_db.pop(index)
            # También eliminar sus items
            global order_items_db
            order_items_db = [item for item in order_items_db if item.order_id != order_id]
            return {"detail": "Order eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Order no encontrado")
