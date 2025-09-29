from typing import List
from datetime import date
from pydantic import BaseModel, Field

# Clientes
class Customer(BaseModel):
    id: int = Field(..., example=1001)
    name: str = Field(..., example="Juan Pérez")
    email: str = Field(..., example="juanperez@gmail.com")

# Productos
class Product(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Nintendo Switch")
    stock: int = Field(..., example=10)
    price: float = Field(..., example=299.99)
    id_Category: int = Field(..., example=1)
    id_supplier: int = Field(..., example=1)

# Descuentos
class Discount(BaseModel):
    id: int = Field(..., example=1)
    id_product: int = Field(..., example=1)
    discount_percentage: float = Field(..., example=0.15)
    flag: bool = Field(..., example=True)  # True = activo, False = inactivo

#Category
class Category(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Electrónicos")
    description: str = Field(..., example="Consolas de Juegos")

#Supplier
class Supplier(BaseModel):
    id: int = Field(..., example=1)#
    name: str = Field(..., example="Proveedor XYZ")
    contact_info: str = Field(..., example="contacto@proveedorxyz.com")
    
#Order
class Order(BaseModel):
    id: int = Field(..., example=1)
    customer_id: int = Field(..., example=1000)
    order_date: date = Field(..., example="2025-09-28")
    total: float = Field(..., example=499.98)
    status: str = Field(..., example="Pendiente")

#OrderItem
class OrderItem(BaseModel):
    id: int = Field(..., example=1)
    order_id: int = Field(..., example=1)
    product_id: int = Field(..., example=2)
    quantity: int = Field(..., example=2)
    price: float = Field(..., example=299.99)
