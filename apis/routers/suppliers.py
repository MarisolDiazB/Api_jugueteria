from fastapi import APIRouter, HTTPException, Query
from typing import List
from models import Supplier
from db import suppliers_db

router = APIRouter(
    prefix="/suppliers",
    tags=["Proveedores"]
)

@router.get("", response_model=List[Supplier])
def get_all_suppliers():
    return suppliers_db

@router.get("/filter", response_model=List[Supplier])
def filter_suppliers(name: str | None = Query(None)):
    if name:
        filtered = [p for p in suppliers_db if p.name.lower() == name.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="No se encontraron proveedores con ese nombre")
        return filtered
    return suppliers_db

@router.get("/{supplier_id}", response_model=Supplier)
def get_supplier_by_id(supplier_id: int):
    for proveedor in suppliers_db:
        if proveedor.id == supplier_id:
            return proveedor
    raise HTTPException(status_code=404, detail="Proveedor no encontrado")

@router.post("", status_code=201, response_model=Supplier)
def crear_supplier(supplier: Supplier):
    for p in suppliers_db:
        if p.id == supplier.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
        if p.name.lower() == supplier.name.lower():
            raise HTTPException(status_code=400, detail="La proveedor ya existe con ese nombre")
    suppliers_db.append(supplier)
    return supplier

@router.put("/{supplier_id}", response_model=Supplier)
def actualizar_supplier(supplier_id: int, update_supplier: Supplier):
    for index, proveedor_existente in enumerate(suppliers_db):
        if proveedor_existente.id == supplier_id:
            # 🔒 Blindar ID
            if update_supplier.id != proveedor_existente.id:
                raise HTTPException(status_code=400, detail="El ID no se puede modificar")
            suppliers_db[index] = update_supplier
            return update_supplier
    raise HTTPException(status_code=404, detail="Proveedor no encontrada")

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int):
    for index, proveedor_existente in enumerate(suppliers_db):
        if proveedor_existente.id == supplier_id:
            suppliers_db.pop(index)
            return {"description": "Proveedor eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Proveedor no encontrado")
