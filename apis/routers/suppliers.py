"""
Módulo de gestión de proveedores.
---------------------------------

Proporciona endpoints REST para listar, crear, actualizar y eliminar proveedores
en la base de datos. Todos los endpoints están protegidos mediante autenticación
JWT usando la dependencia `get_current_user`.

Incluye validaciones para:
    - Evitar nombres duplicados de proveedores.
    - Permitir actualizaciones parciales (PATCH).
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_db
from apis.models import Supplier
from apis.schemas import SupplierIn, SupplierOut, SupplierUpdate
from apis.routers.auth import get_current_user

router = APIRouter(prefix="/suppliers", tags=["Proveedores"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[SupplierOut])
def list_suppliers(q: str | None = Query(None), db: Session = Depends(get_db)):
    """Obtiene una lista de proveedores registrados, con opción de filtrado por nombre.

    Args:
        q (str | None): Texto opcional para filtrar por nombre (insensible a mayúsculas/minúsculas).
        db (Session): Sesión activa de SQLAlchemy.

    Returns:
        list[SupplierOut]: Lista de proveedores ordenada alfabéticamente.
    """
    query = db.query(Supplier)
    if q:
        query = query.filter(func.lower(Supplier.name).like(f"%{q.lower()}%"))
    return query.order_by(Supplier.name).all()

@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    """Obtiene un proveedor específico por su ID.

    Args:
        supplier_id (UUID): Identificador único del proveedor.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el proveedor no existe.

    Returns:
        SupplierOut: Datos del proveedor encontrado.
    """
    obj = db.get(Supplier, supplier_id)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    return obj

@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierIn, db: Session = Depends(get_db)):
    """Crea un nuevo proveedor verificando que no exista un nombre duplicado.

    Args:
        payload (SupplierIn): Datos del nuevo proveedor.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 409: Si ya existe un proveedor con el mismo nombre.

    Returns:
        SupplierOut: Proveedor creado exitosamente.
    """
    if db.query(Supplier).filter(func.lower(Supplier.name) == payload.name.lower()).first():
        raise HTTPException(409, "El proveedor ya existe con ese nombre")
    obj = Supplier(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: UUID, payload: SupplierIn, db: Session = Depends(get_db)):
    """Actualiza completamente los datos de un proveedor existente.

    Args:
        supplier_id (UUID): ID del proveedor a actualizar.
        payload (SupplierIn): Nuevos datos del proveedor.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si el proveedor no existe.
            - 409: Si otro proveedor ya usa el mismo nombre.

    Returns:
        SupplierOut: Proveedor actualizado correctamente.
    """
    obj = db.get(Supplier, supplier_id)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    conflict = db.query(Supplier).filter(
        func.lower(Supplier.name) == payload.name.lower(), Supplier.id != supplier_id
    ).first()
    if conflict:
        raise HTTPException(409, "Otro proveedor ya usa ese nombre")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{supplier_id}", response_model=SupplierOut)
def patch_supplier(supplier_id: UUID, payload: SupplierUpdate, db: Session = Depends(get_db)):
    """Actualiza parcialmente los campos de un proveedor existente (PATCH).

    Solo se modifican los campos enviados en el cuerpo de la solicitud.

    Args:
        supplier_id (UUID): Identificador del proveedor a modificar.
        payload (SupplierUpdate): Campos opcionales a actualizar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si el proveedor no existe.
            - 409: Si el nuevo nombre ya está en uso.

    Returns:
        SupplierOut: Proveedor actualizado parcialmente.
    """
    obj = db.get(Supplier, supplier_id)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        conflict = db.query(Supplier).filter(
            func.lower(Supplier.name) == data["name"].lower(), Supplier.id != supplier_id
        ).first()
        if conflict:
            raise HTTPException(409, "Otro proveedor ya usa ese nombre")
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    """Elimina un proveedor existente de la base de datos.

    Args:
        supplier_id (UUID): Identificador único del proveedor.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el proveedor no existe.

    Returns:
        None
    """
    obj = db.get(Supplier, supplier_id)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    db.delete(obj); db.commit()
