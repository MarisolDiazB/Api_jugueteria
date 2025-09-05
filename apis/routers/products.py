from fastapi import APIRouter, HTTPException, Query
from typing import List
from models import Product
from db import products_db

router = APIRouter(
    prefix="/products",
    tags=["Productos"]
)

@router.get("", response_model=List[Product])
def get_all_products():
    return products_db

@router.get("/filter", response_model=List[Product])
def filter_products(category: str | None = Query(None)):
    if category:
        filtered = [p for p in products_db if p.category.lower() == category.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="No se encontraron productos con esa categoría")
        return filtered
    return products_db

@router.get("/{product_id}", response_model=Product)
def get_product_by_id(product_id: int):
    for producto in products_db:
        if producto.id == product_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("", status_code=201, response_model=Product)
def crear_product(product: Product):
    for p in products_db:
        if p.id == product.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
        if p.name.lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="El producto ya existe con ese nombre")
    products_db.append(product)
    return product

@router.put("/{product_id}", response_model=Product)
def actualizar_product(product_id: int, update_product: Product):
    for index, producto_existente in enumerate(products_db):
        if producto_existente.id == product_id:
            # 🔒 Blindar ID
            if update_product.id != producto_existente.id:
                raise HTTPException(status_code=400, detail="El ID no se puede modificar")
            products_db[index] = update_product
            return update_product
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.delete("/{product_id}")
def delete_product(product_id: int):
    for index, producto_existente in enumerate(products_db):
        if producto_existente.id == product_id:
            products_db.pop(index)
            return {"description": "producto eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")
