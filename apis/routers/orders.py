"""
Módulo de gestión de órdenes.
-----------------------------

Proporciona endpoints REST para listar, crear, actualizar y eliminar órdenes
en la base de datos. Cada orden se asocia a un cliente y puede incluir un descuento.

Todos los endpoints están protegidos con autenticación JWT mediante la dependencia
`get_current_user`.

Incluye validaciones para:
    - Existencia del cliente (`customer_id`).
    - Existencia del descuento (`discount_id`) si se proporciona.
"""
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
    """Obtiene todas las órdenes registradas, ordenadas por fecha de creación descendente.

    Args:
        db (Session): Sesión activa de SQLAlchemy.

    Returns:
        list[OrderOut]: Lista de órdenes registradas en el sistema.
    """
    return db.query(Order).order_by(Order.fecha_creacion.desc()).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    """Obtiene una orden específica por su identificador único.

    Args:
        order_id (UUID): ID de la orden a buscar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si la orden no existe en la base de datos.

    Returns:
        OrderOut: Datos de la orden encontrada.
    """
    obj = db.get(Order, order_id)
    if not obj: raise HTTPException(404, "Orden no encontrada")
    return obj

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    """Crea una nueva orden validando la existencia del cliente y del descuento.

    Args:
        payload (OrderIn): Datos de la nueva orden a registrar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 400: Si el `customer_id` o `discount_id` no son válidos.

    Returns:
        OrderOut: Orden creada exitosamente.
    """
    if not db.get(Customer, payload.customer_id):
        raise HTTPException(400, "customer_id inválido")
    if payload.discount_id and not db.get(Discount, payload.discount_id):
        raise HTTPException(400, "discount_id inválido")
    obj = Order(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: UUID, payload: OrderIn, db: Session = Depends(get_db)):
    """Actualiza completamente una orden existente.

    Args:
        order_id (UUID): Identificador de la orden a actualizar.
        payload (OrderIn): Nuevos datos para la orden.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si la orden no existe.
            - 400: Si el cliente o el descuento no son válidos.

    Returns:
        OrderOut: Orden actualizada correctamente.
    """
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
    
    """Actualiza parcialmente los campos de una orden existente.

    Solo modifica los campos enviados en la solicitud.  
    Se validan las claves foráneas (`customer_id`, `discount_id`) si están presentes.

    Args:
        order_id (UUID): ID de la orden a modificar.
        payload (OrderUpdate): Campos opcionales a actualizar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si la orden no existe.
            - 400: Si `customer_id` o `discount_id` son inválidos.

    Returns:
        OrderOut: Orden modificada parcialmente.
    """
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
    """Elimina una orden existente de la base de datos.

    Args:
        order_id (UUID): Identificador único de la orden a eliminar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si la orden no existe.

    Returns:
        None
    """
    obj = db.get(Order, order_id)
    if not obj: raise HTTPException(404, "Orden no encontrada")
    db.delete(obj); db.commit()
