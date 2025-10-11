"""
Módulo de gestión de ítems de órdenes.
-------------------------------------

Proporciona endpoints REST para listar, crear, actualizar y eliminar los ítems
(asociaciones entre pedidos y productos) de la base de datos.  
Todos los endpoints requieren autenticación JWT mediante la dependencia `get_current_user`.

Incluye validaciones para:
    - Verificar que el `order_id` y `product_id` existan.
    - Actualizar ítems de forma total o parcial (PUT y PATCH).
"""
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
    """Obtiene una lista de todos los ítems de orden registrados.

    Args:
        db (Session): Sesión activa de SQLAlchemy.

    Returns:
        list[OrderItemOut]: Lista de ítems de orden ordenados por fecha de creación (descendente).
    """
    return db.query(OrderItem).order_by(OrderItem.fecha_creacion.desc()).all()

@router.get("/{item_id}", response_model=OrderItemOut)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    """Obtiene un ítem de orden específico según su ID.

    Args:
        item_id (UUID): Identificador único del ítem.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el ítem no existe.

    Returns:
        OrderItemOut: Datos del ítem encontrado.
    """
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    return obj

@router.post("/", response_model=OrderItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: OrderItemIn, db: Session = Depends(get_db)):
    """Crea un nuevo ítem de orden validando la existencia del pedido y producto.

    Args:
        payload (OrderItemIn): Datos del ítem a crear.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 400: Si el `order_id` o `product_id` no existen.

    Returns:
        OrderItemOut: Ítem de orden creado correctamente.
    """
    if not db.get(Order, payload.order_id):
        raise HTTPException(400, "order_id inválido")
    if not db.get(Product, payload.product_id):
        raise HTTPException(400, "product_id inválido")
    obj = OrderItem(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{item_id}", response_model=OrderItemOut)
def update_item(item_id: UUID, payload: OrderItemIn, db: Session = Depends(get_db)):
    """Actualiza completamente un ítem de orden existente.

    Args:
        item_id (UUID): ID del ítem a actualizar.
        payload (OrderItemIn): Nuevos datos del ítem (reemplaza todos los campos).
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si el ítem no existe.
            - 400: Si los IDs de orden o producto son inválidos.

    Returns:
        OrderItemOut: Ítem de orden actualizado.
    """
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
    """Actualiza parcialmente un ítem de orden (PATCH).

    Solo se modifican los campos enviados en la solicitud.

    Args:
        item_id (UUID): Identificador único del ítem.
        payload (OrderItemUpdate): Campos opcionales a modificar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el ítem no existe.

    Returns:
        OrderItemOut: Ítem de orden actualizado parcialmente.
    """
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: UUID, db: Session = Depends(get_db)):  
    """Elimina un ítem de orden de la base de datos.

    Args:
        item_id (UUID): Identificador del ítem a eliminar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el ítem no existe.

    Returns:
        None
    """
    obj = db.get(OrderItem, item_id)
    if not obj: raise HTTPException(404, "Item no encontrado")
    db.delete(obj); db.commit()
