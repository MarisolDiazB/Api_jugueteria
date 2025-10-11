"""
Aplicación principal de la API Juguetería 🎮
--------------------------------------------

Este módulo inicializa la aplicación FastAPI, configura los middlewares,
define la ruta raíz ("/") y registra todos los routers de la API.

Routers incluidos:
    - Autenticación (auth)
    - Clientes (customers)
    - Categorías (categories)
    - Proveedores (suppliers)
    - Productos (products)
    - Descuentos (discounts)
    - Órdenes (orders)
    - Ítems de orden (order_items)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis.routers import auth, customers, categories, suppliers, products, discounts, orders, order_items


app = FastAPI(title="API Juguetería")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"mensaje": "Hola Juguetería 🚀"}




app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(discounts.router)
app.include_router(orders.router)
app.include_router(order_items.router)


