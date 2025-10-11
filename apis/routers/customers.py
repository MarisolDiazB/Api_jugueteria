"""
Módulo de gestión de clientes.
------------------------------

Proporciona endpoints REST para listar, crear, actualizar, filtrar y eliminar
clientes registrados en la base de datos. Implementa paginación, filtros por
nombre o email, y validación de duplicados en el correo electrónico.
"""
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
    limit: int = Query(50, ge=1, le=200,description="Cantidad máxima de resultados"),
    offset: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    db: Session = Depends(get_db),
):
    """Lista los clientes con soporte de búsqueda y paginación.

    Args:
        q (Optional[str]): Texto opcional para filtrar por nombre o correo electrónico.
        limit (int): Límite máximo de resultados (por defecto 50, máx. 200).
        offset (int): Desplazamiento para la paginación.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si no se encuentran clientes en la base de datos.

    Returns:
        List[CustomerOut]: Lista de clientes encontrados.
    """
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
    
    """Obtiene un cliente específico por su ID.

    Args:
        customer_id (UUID): Identificador único del cliente.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el cliente no existe.

    Returns:
        CustomerOut: Datos del cliente encontrado.
    """
    entity = db.get(Customer, customer_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return entity


@router.get("/filter/by-email", response_model=List[CustomerOut])
def filter_by_email(email: str = Query(...), db: Session = Depends(get_db)):
    
    """Filtra los clientes que tienen un correo electrónico específico.

    Args:
        email (str): Correo electrónico a buscar (insensible a mayúsculas/minúsculas).
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si no se encuentran clientes con ese correo.

    Returns:
        List[CustomerOut]: Lista de clientes que coinciden con el correo.
    """
    stmt = select(Customer).where(func.lower(Customer.email) == email.lower())
    rows = db.execute(stmt).scalars().all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron clientes con ese correo")
    return rows


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db)):
    """Crea un nuevo cliente validando que el correo no esté registrado.

    Args:
        payload (CustomerIn): Datos del nuevo cliente.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el correo electrónico ya está en uso.

    Returns:
        CustomerOut: Cliente creado y guardado en la base de datos.
    """
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
    """Actualiza los datos completos de un cliente existente.

    Args:
        customer_id (UUID): ID del cliente a actualizar.
        payload (CustomerUpdate): Nuevos datos del cliente.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si el cliente no existe.
            - 400: Si el nuevo correo ya está registrado por otro cliente.

    Returns:
        CustomerOut: Cliente actualizado con los nuevos valores.
    """
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
    """Elimina un cliente existente de la base de datos.

    Args:
        customer_id (UUID): Identificador único del cliente a eliminar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el cliente no existe.

    Returns:
        None
    """
    entity = db.get(Customer, customer_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    db.delete(entity)
    db.commit()
