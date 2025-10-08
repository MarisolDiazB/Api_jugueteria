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
    query = db.query(Category)
    if q:
       
        query = query.filter(func.lower(Category.name) == func.lower(q))
      
    return query.order_by(Category.name).all()

@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return obj

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryIn, db: Session = Depends(get_db)):
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
