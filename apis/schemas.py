from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr
from pydantic import BaseModel, EmailStr, Field





class AuditBase(BaseModel):
    creado_por: str = "api"
    actualizado_por: str = "api"


class CategoryIn(AuditBase):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    actualizado_por: str = "api"

class CategoryOut(CategoryIn):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}

class SupplierIn(AuditBase):
    name: str
    contact_info: Optional[str] = None

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    actualizado_por: str = "api"

class SupplierOut(SupplierIn):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class ProductIn(AuditBase):
    name: str
    stock: int = Field(ge=0)
    price: Decimal = Field(ge=0)          
    category_id: UUID
    supplier_id: UUID

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    price: Optional[Decimal] = Field(default=None, ge=0)
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    actualizado_por: str = "api"

class ProductOut(ProductIn):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class CustomerIn(AuditBase):
    name: str
    email: EmailStr                      

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    actualizado_por: str = "api"

class CustomerOut(CustomerIn):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class DiscountIn(AuditBase):
    product_id: UUID
    discount_percentage: Decimal = Field(ge=0, le=100)  
    flag: bool = False

class DiscountUpdate(BaseModel):
    product_id: Optional[UUID] = None
    discount_percentage: Optional[Decimal] = Field(default=None, ge=0, le=100)
    flag: Optional[bool] = None
    actualizado_por: str = "api"

class DiscountOut(DiscountIn):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class OrderItemIn(AuditBase):
    order_id: UUID
    product_id: UUID
    quantity: int = Field(ge=1)
    price: Decimal = Field(ge=0)          

class OrderItemUpdate(BaseModel):
    product_id: Optional[UUID] = None
    quantity: Optional[int] = Field(default=None, ge=1)
    price: Optional[Decimal] = Field(default=None, ge=0)
    actualizado_por: str = "api"

class OrderItemOut(OrderItemIn):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}


class OrderIn(AuditBase):
    customer_id: UUID
    status: str = "pendiente"

class OrderUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    status: Optional[str] = None
    actualizado_por: str = "api"

class OrderOut(OrderIn):
    id: UUID
    total: Decimal                        
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}

class UserCreate(AuditBase):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

class UserOut(AuditBase):
    id: UUID
    email: EmailStr
    is_active: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}
