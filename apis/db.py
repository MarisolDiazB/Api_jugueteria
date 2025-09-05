from typing import List
from models import Customer, Product, Discount

# Clientes simulados
customer_db: List[Customer] = [
    Customer(id=1000, name="Juanito Perez", email="Juanito123@gmail.com"),
    Customer(id=2000, name="Marisol Perez", email="Marisol123@gmail.com")
]

# Productos
products_db: List[Product] = [
    Product(id=1, name="Nintendo Switch", stock=5, price=500.0, category="Tecnologia"),
    Product(id=2, name="Castillo Barbie", stock=10, price=50.0, category="Juguetes")
]

# Descuentos
discounts_db: List[Discount] = [
    Discount(id=1, id_product=1, discount_percentage=0.15, flag=False),
    Discount(id=2, id_product=2, discount_percentage=0.10, flag=True)
]
