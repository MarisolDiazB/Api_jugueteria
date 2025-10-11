"""
Módulo de gestión de categorías.
--------------------------------

Este router maneja las operaciones CRUD para las categorías de productos en la API.
Incluye protección mediante autenticación JWT, validación de nombres duplicados
y consultas filtradas insensibles a mayúsculas/minúsculas.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apis.models import Category
from apis.schemas import CategoryIn, CategoryOut, CategoryUpdate
from apis.routers.auth import get_current_user
from database.connection import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categorias"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=list[CategoryOut])
def list_categories(
    q: str | None = Query(None, description="Filtra por nombre (case-insensitive)"),
   
    db: Session = Depends(get_db),
):
    """Obtiene una lista de todas las categorías registradas.

    Args:
        q (str | None): Texto opcional para filtrar categorías por nombre.
        db (Session): Sesión activa de la base de datos.

    Returns:
        list[CategoryOut]: Lista de categorías ordenadas por nombre.
    """
    query = db.query(Category)
    if q:
       
        query = query.filter(func.lower(Category.name) == func.lower(q))
      
    return query.order_by(Category.name).all()

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: UUID, db: Session = Depends(get_db)):
    """Obtiene una categoría específica por su ID.

    Args:
        category_id (UUID): Identificador único de la categoría.
        db (Session): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si no se encuentra la categoría.

    Returns:
        CategoryOut: Datos de la categoría encontrada.
    """
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return obj

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryIn, db: Session = Depends(get_db)):
    """Crea una nueva categoría, validando que no exista un nombre duplicado.

    Args:
        payload (CategoryIn): Datos de entrada para la nueva categoría.
        db (Session): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si ya existe una categoría con el mismo nombre.

    Returns:
        CategoryOut: Categoría creada y registrada en la base de datos.
    """
    conflict = (
        db.query(Category)
        .filter(func.lower(Category.name) == func.lower(payload.name))
        .first()
    )
    if conflict:
        raise HTTPException(status_code=409, detail="La categoría ya existe con ese nombre")

    obj = Category(
        name=payload.name,
        description=payload.description,
        creado_por=payload.creado_por,
        actualizado_por=payload.actualizado_por,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: UUID, payload: CategoryIn, db: Session = Depends(get_db)):
    """Actualiza todos los campos de una categoría existente.

    Args:
        category_id (UUID): ID de la categoría a actualizar.
        payload (CategoryIn): Nuevos datos de la categoría.
        db (Session): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si la categoría no existe o el nombre ya está en uso.

    Returns:
        CategoryOut: Categoría actualizada con los nuevos valores.
    """
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    conflict = (
        db.query(Category)
        .filter(func.lower(Category.name) == func.lower(payload.name), Category.id != category_id)
        .first()
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Otra categoría ya usa ese nombre")

    obj.name = payload.name
    obj.description = payload.description
    obj.actualizado_por = payload.actualizado_por
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{category_id}", response_model=CategoryOut)
def patch_category(category_id: UUID, payload: CategoryUpdate, db: Session = Depends(get_db)):
    
    """Actualiza parcialmente una categoría existente.

    Solo modifica los campos enviados en el cuerpo de la solicitud.
    Permite cambiar nombre y descripción con validación de duplicados.

    Args:
        category_id (UUID): ID de la categoría a modificar.
        payload (CategoryUpdate): Campos a actualizar (parciales).
        db (Session): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si la categoría no existe o hay conflicto de nombre.

    Returns:
        CategoryOut: Categoría actualizada con los nuevos valores.
    """
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if payload.name is not None:
        conflict = (
            db.query(Category)
            .filter(func.lower(Category.name) == func.lower(payload.name), Category.id != category_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=409, detail="Otra categoría ya usa ese nombre")
        obj.name = payload.name

    if payload.description is not None:
        obj.descri
