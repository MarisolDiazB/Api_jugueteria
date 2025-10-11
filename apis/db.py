"""
Base de datos simulada (mock data) para la API de Juguetería.
-------------------------------------------------------------

Este módulo contiene listas de objetos que simulan registros en la base de datos,
utilizadas para pruebas locales o demostraciones cuando aún no se conecta
una base de datos real (SQL Server o MySQL).

Incluye entidades:
    - Customer (Clientes)
    - Product (Productos)
    - Discount (Descuentos)
    - Category (Categorías)
    - Supplier (Proveedores)
    - Order (Órdenes)
    - OrderItem (Ítems de órdenes)
"""
from typing import List
from datetime import date
from models import Category, Customer, Product, Discount, Supplier, Order, OrderItem


customer_db: List[Customer] = [
    Customer(id=1000, name="Juanito Perez", email="Juanito123@gmail.com"),
    Customer(id=2000, name="Marisol Perez", email="Marisol123@gmail.com")
]


products_db: List[Product] = [
    Product(id=1, name="Nintendo Switch", stock=5, price=500.0, id_Category=1,id_supplier=1),
    Product(id=2, name="Castillo Barbie", stock=10, price=50.0, id_Category=1,id_supplier=1)
]


discounts_db: List[Discount] = [
    Discount(id=1, id_product=1, discount_percentage=0.15, flag=False),
    Discount(id=2, id_product=2, discount_percentage=0.10, flag=True)
]


categories_db: List[Category] = [
    Category(id=1, name="Muñecas", description="hecha para niñas de 5 años en adelante"),
    Category(id=2, name="Carros", description="hecha para niños o niñas de 5 años en adelante")
]


suppliers_db: List[Supplier] = [
    Supplier(id=1, name="Hashbro", contact_info="Hashbro123@gmail.com"),
    Supplier(id=2, name="Mattel", contact_info="Hashbro123@gmail.com")
]


orders_db: List[Order] = [
    Order(id=1, customer_id=1000, order_date=date(2025, 9, 28), total=499.98, status="pendiente"),
    Order(id=2, customer_id=2000, order_date=date(2025, 9, 28), total=199.99, status="pagado"),
]



order_items_db: List[OrderItem] = [
    OrderItem(id=1, order_id=1, product_id=1, quantity=1, price=299.99),
    OrderItem(id=2, order_id=1, product_id=2, quantity=1, price=199.99),
    OrderItem(id=3, order_id=2, product_id=2, quantity=1, price=199.99),
]



