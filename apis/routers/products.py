"""
Módulo de gestión de productos.
-------------------------------

Proporciona endpoints REST para listar, crear, actualizar y eliminar productos
de la base de datos. Cada producto está asociado a una categoría y un proveedor.

Todos los endpoints están protegidos con autenticación JWT mediante
`get_current_user`.

Incluye validaciones para:
    - Evitar duplicados por nombre de producto.
    - Verificar la existencia de `category_id` y `supplier_id`.
    - Permitir actualizaciones parciales (PATCH).
"""
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
    
    """Obtiene una lista de productos, con opción de búsqueda por nombre.

    Args:
        q (str | None): Texto opcional para filtrar productos por nombre (no sensible a mayúsculas/minúsculas).
        db (Session): Sesión activa de SQLAlchemy.

    Returns:
        list[ProductOut]: Lista de productos ordenada alfabéticamente.
    """
    query = db.query(Product)
    if q:
        query = query.filter(func.lower(Product.name).like(f"%{q.lower()}%"))
    return query.order_by(Product.name).all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Obtiene los datos de un producto específico por su ID.

    Args:
        product_id (UUID): Identificador único del producto.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el producto no existe.

    Returns:
        ProductOut: Datos del producto encontrado.
    """
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    return obj

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    """Crea un nuevo producto verificando duplicados y relaciones válidas.

    Args:
        payload (ProductIn): Datos del nuevo producto.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 400: Si `category_id` o `supplier_id` son inválidos.
            - 409: Si ya existe un producto con el mismo nombre.

    Returns:
        ProductOut: Producto creado con éxito.
    """
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
    """Actualiza todos los campos de un producto existente.

    Args:
        product_id (UUID): ID del producto a actualizar.
        payload (ProductIn): Nuevos datos del producto.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si el producto no existe.
            - 400: Si las claves foráneas son inválidas.
            - 409: Si otro producto usa el mismo nombre.

    Returns:
        ProductOut: Producto actualizado correctamente.
    """
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
    """Actualiza parcialmente un producto existente (PATCH).

    Solo modifica los campos enviados en el cuerpo de la solicitud.

    Args:
        product_id (UUID): Identificador del producto.
        payload (ProductUpdate): Campos opcionales a actualizar.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException:
            - 404: Si el producto no existe.
            - 400: Si `category_id` o `supplier_id` son inválidos.
            - 409: Si otro producto usa el mismo nombre.

    Returns:
        ProductOut: Producto actualizado parcialmente.
    """
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
    """Elimina un producto existente de la base de datos.

    Args:
        product_id (UUID): Identificador único del producto.
        db (Session): Sesión activa de SQLAlchemy.

    Raises:
        HTTPException: Si el producto no existe.

    Returns:
        None
    """
    obj = db.get(Product, product_id)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    db.delete(obj); db.commit()
