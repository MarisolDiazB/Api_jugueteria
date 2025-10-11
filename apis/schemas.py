"""
Esquemas Pydantic para la API de Juguetería.
============================================

Define las clases de entrada y salida para cada entidad del sistema
(Categorías, Proveedores, Productos, Clientes, Descuentos, Órdenes y Usuarios).

Todos los esquemas heredan de `BaseModel` y validan datos de entrada/salida.
Incluyen campos de auditoría (`creado_por`, `actualizado_por`), validaciones
numéricas, tipos estrictos y compatibilidad con `from_attributes=True`
para conversión automática desde ORM (SQLAlchemy).
"""
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr
from pydantic import BaseModel, EmailStr, Field





class AuditBase(BaseModel):
    """Campos de auditoría comunes a todas las entidades."""
    creado_por: str = "api"
    actualizado_por: str = "api"


class CategoryIn(AuditBase):
    """Datos de entrada para crear una categoría."""
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    """Datos opcionales para actualizar una categoría (PATCH)."""
    name: Optional[str] = None
    description: Optional[str] = None
    actualizado_por: str = "api"

class CategoryOut(CategoryIn):
    """Datos de salida de una categoría."""
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}

class SupplierIn(AuditBase):
    """Datos de entrada para crear un proveedor."""
    name: str
    contact_info: Optional[str] = None

class SupplierUpdate(BaseModel):
    """Datos opcionales para actualizar un proveedor."""
    name: Optional[str] = None
    contact_info: Optional[str] = None
    actualizado_por: str = "api"

class SupplierOut(SupplierIn):
    """Datos de salida de un proveedor."""
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class ProductIn(AuditBase):
    """Datos de entrada para crear un producto."""
    name: str
    stock: int = Field(ge=0, description="Cantidad en inventario (>= 0)")
    price: Decimal = Field(ge=0, description="Precio unitario del producto (>= 0)")       
    category_id: UUID
    supplier_id: UUID

class ProductUpdate(BaseModel):
    """Datos opcionales para actualizar un producto."""
    name: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    price: Optional[Decimal] = Field(default=None, ge=0)
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    actualizado_por: str = "api"

class ProductOut(ProductIn):
    """Datos de salida de un producto."""
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class CustomerIn(AuditBase):
    """Datos de entrada para registrar un cliente."""
    name: str
    email: EmailStr                      

class CustomerUpdate(BaseModel):
    """Datos opcionales para actualizar un cliente."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    actualizado_por: str = "api"

class CustomerOut(CustomerIn):
    """Datos de salida de un cliente."""
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class DiscountIn(AuditBase):
    """Datos de entrada para crear un descuento asociado a un producto."""
    product_id: UUID
    discount_percentage: Decimal = Field(ge=0, le=100, description="Porcentaje de descuento (0-100)") 
    flag: bool = False

class DiscountUpdate(BaseModel):
    """Datos opcionales para actualizar un descuento."""
    product_id: Optional[UUID] = None
    discount_percentage: Optional[Decimal] = Field(default=None, ge=0, le=100)
    flag: Optional[bool] = None
    actualizado_por: str = "api"

class DiscountOut(DiscountIn):
    """Datos de salida de un descuento."""
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class OrderItemIn(AuditBase):
    """Datos de entrada para crear un ítem dentro de una orden."""
    order_id: UUID
    product_id: UUID
    quantity: int = Field(ge=1,description="Cantidad del producto en la orden (>=1)")
    price: Decimal = Field(ge=0,description="Precio unitario del producto (>=0)")
        

class OrderItemUpdate(BaseModel):
    """Datos opcionales para actualizar un ítem de orden."""
    product_id: Optional[UUID] = None
    quantity: Optional[int] = Field(default=None, ge=1)
    price: Optional[Decimal] = Field(default=None, ge=0)
    actualizado_por: str = "api"

class OrderItemOut(OrderItemIn):
    """Datos de salida de un ítem de orden."""
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class OrderIn(AuditBase):
    """Datos de entrada para registrar una orden."""
    customer_id: UUID
    status: str = "pendiente"

class OrderUpdate(BaseModel):
    """Datos opcionales para actualizar una orden."""
    customer_id: Optional[UUID] = None
    status: Optional[str] = None
    actualizado_por: str = "api"

class OrderOut(OrderIn):
    """Datos de salida de una orden."""
    id: UUID
    total: Decimal                        
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}

class UserCreate(AuditBase):
    """Datos de entrada para registrar un nuevo usuario."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

class UserOut(AuditBase):
    """Datos de salida de un usuario."""
    id: UUID
    email: EmailStr
    is_active: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}

