from fastapi import APIRouter, HTTPException
from typing import List
from models import OrderItem
from db import order_items_db, orders_db, products_db

router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)

# Obtener todos los items
@router.get("", response_model=List[OrderItem])
def get_all_order_items():
    return order_items_db

# Obtener items por order_id
@router.get("/order/{order_id}", response_model=List[OrderItem])
def get_items_by_order(order_id: int):
    items = [item for item in order_items_db if item.order_id == order_id]
    if not items:
        raise HTTPException(status_code=404, detail="No hay items para este pedido")
    return items

# Agregar item a un pedido
@router.post("", response_model=OrderItem, status_code=201)
def add_order_item(order_item: OrderItem):
    # Validar id
    for item in order_items_db:
        if item.id == order_item.id:
            raise HTTPException(status_code=400, detail="El ID del item ya existe")
    # Validar pedido 
    if not any(order.id == order_item.order_id for order in orders_db):
        raise HTTPException(status_code=404, detail="El pedido no existe")
    # Validar producto
    if not any(product.id == order_item.product_id for product in products_db):
        raise HTTPException(status_code=404, detail="El producto no existe")
    order_items_db.append(order_item)
    return order_item

# Actualizar item de pedido
@router.put("/{item_id}", response_model=OrderItem)
def update_order_item(item_id: int, update_item: OrderItem):
    for index, item in enumerate(order_items_db):
        if item.id == item_id:
            # 🔒 No cambiar ID
            if update_item.id != item_id:
                raise HTTPException(status_code=400, detail="No se puede modificar el ID")
            order_items_db[index] = update_item
            return update_item
    raise HTTPException(status_code=404, detail="Item no encontrado")

# Eliminar item de pedido
@router.delete("/{item_id}")
def delete_order_item(item_id: int):
    for index, item in enumerate(order_items_db):
        if item.id == item_id:
            order_items_db.pop(index)
            return {"detail": "Item eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Item no encontrado")
