from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_db
from apis.models import Product, Category, Supplier
from apis.schemas import ProductIn, ProductOut, ProductUpdate
from apis.routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["Productos"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=list[ProductOut])
def list_products(q: str | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Product)
    if q:
        query = query.filter(func.lower(Product.name).like(f"%{q.lower()}%"))
    return query.order_by(Product.name).all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    return obj

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    if not db.get(Category, payload.category_id):
        raise HTTPException(400, "category_id inválido")
    if not db.get(Supplier, payload.supplier_id):
        raise HTTPException(400, "supplier_id inválido")
    if db.query(Product).filter(func.lower(Product.name) == payload.name.lower()).first():
        raise HTTPException(409, "El producto ya existe con ese nombre")
    obj = Product(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: UUID, payload: ProductIn, db: Session = Depends(get_db)):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    if not db.get(Category, payload.category_id):
        raise HTTPException(400, "category_id inválido")
    if not db.get(Supplier, payload.supplier_id):
        raise HTTPException(400, "supplier_id inválido")
    conflict = db.query(Product).filter(
        func.lower(Product.name) == payload.name.lower(), Product.id != product_id
    ).first()
    if conflict:
        raise HTTPException(409, "Otro producto ya usa ese nombre")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.patch("/{product_id}", response_model=ProductOut)
def patch_product(product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db)):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        conflict = db.query(Product).filter(
            func.lower(Product.name) == data["name"].lower(), Product.id != product_id
        ).first()
        if conflict:
            raise HTTPException(409, "Otro producto ya usa ese nombre")
    if "category_id" in data and data["category_id"] and not db.get(Category, data["category_id"]):
        raise HTTPException(400, "category_id inválido")
    if "supplier_id" in data and data["supplier_id"] and not db.get(Supplier, data["supplier_id"]):
        raise HTTPException(400, "supplier_id inválido")
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    db.delete(obj); db.commit()
