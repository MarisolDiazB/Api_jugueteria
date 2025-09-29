from fastapi import APIRouter, HTTPException, Query
from typing import List
from models import Category
from db import categories_db

router = APIRouter(
    prefix="/categories",
    tags=["Categorias"]
)

@router.get("", response_model=List[Category])
def get_all_categories():
    return categories_db

@router.get("/filter", response_model=List[Category])
def filter_categories(name: str | None = Query(None)):
    if name:
        filtered = [p for p in categories_db if p.name.lower() == name.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="No se encontraron categorias con ese nombre")
        return filtered
    return categories_db

@router.get("/{category_id}", response_model=Category)
def get_category_by_id(category_id: int):
    for categoria in categories_db:
        if categoria.id == category_id:
            return categoria
    raise HTTPException(status_code=404, detail="Categoria no encontrado")

@router.post("", status_code=201, response_model=Category)
def crear_category(category: Category):
    for p in categories_db:
        if p.id == category.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
        if p.name.lower() == category.name.lower():
            raise HTTPException(status_code=400, detail="La categoria ya existe con ese nombre")
    categories_db.append(category)
    return category

@router.put("/{category_id}", response_model=Category)
def actualizar_category(category_id: int, update_category: Category):
    for index, categoria_existente in enumerate(categories_db):
        if categoria_existente.id == category_id:
            # 🔒 Blindar ID
            if update_category.id != categoria_existente.id:
                raise HTTPException(status_code=400, detail="El ID no se puede modificar")
            categories_db[index] = update_category
            return update_category
    raise HTTPException(status_code=404, detail="Categoria no encontrada")

@router.delete("/{category_id}")
def delete_category(category_id: int):
    for index, categoria_existente in enumerate(categories_db):
        if categoria_existente.id == category_id:
            categories_db.pop(index)
            return {"description": "Categoria eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Categoria no encontrado")
