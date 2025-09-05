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
    category: str = Field(..., example="Electrónico")

# Descuentos
class Discount(BaseModel):
    id: int = Field(..., example=1)
    id_product: int = Field(..., example=1)
    discount_percentage: float = Field(..., example=0.15)
    flag: bool = Field(..., example=True)  # True = activo, False = inactivo
