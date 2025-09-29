from fastapi import FastAPI
from routers import customers, products, discounts , categories , suppliers, orders ,order_items


app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "Hola Juguetería 🚀"}

# Incluir routers
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(discounts.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(orders.router)
app.include_router(order_items.router)
