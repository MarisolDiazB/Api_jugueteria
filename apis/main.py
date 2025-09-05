from fastapi import FastAPI
from routers import customers, products, discounts


app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "Hola Juguetería 🚀"}

# Incluir routers
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(discounts.router)
