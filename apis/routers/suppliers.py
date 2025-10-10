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
    query = db.query(Supplier)
    if q:
        query = query.filter(func.lower(Supplier.name).like(f"%{q.lower()}%"))
    return query.order_by(Supplier.name).all()

@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Supplier, supplier_id)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    return obj

@router.post("/", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierIn, db: Session = Depends(get_db)):
    if db.query(Supplier).filter(func.lower(Supplier.name) == payload.name.lower()).first():
        raise HTTPException(409, "El proveedor ya existe con ese nombre")
    obj = Supplier(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: UUID, payload: SupplierIn, db: Session = Depends(get_db)):
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
    obj = db.get(Supplier, supplier_id)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    db.delete(obj); db.commit()
