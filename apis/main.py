from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "Hola Juguetería 🚀"}

# Clientes (id, nombre, Correo)
class Customer(BaseModel):
    id: int 
    name: str 
    email: str 

# productos (id, nombre, stock, precio, categoria)
class Product(BaseModel):
    id: int 
    name: str
    stock: int 
    price: float 
    category: str 

# descuentos (id_producto , porcentaje_descuento , estado)
class Discount(BaseModel):
    id: int 
    discount_percentage: float 
    flag: bool 

#Clientes
# --- Listaao de Clientes ---
customer_db: List[Customer] = [
    Customer(id=1000, name="Juanito Perez", email="Juanito123@gmail.com"),
    Customer(id=2000, name="Marisol Perez", email="Marisol123@gmail.com")
]
@app.get(
    "/customers",#Ruta
    response_model=List[Customer],
    summary="Obtener todos los clientes",
    description="Esto nos devuelve una lista con todos los clientes registrados",
    tags=["Clientes"],
    responses={
        200: {"description": "Lista de clientes recuperada exitosamente"}
    }
)
def get_all_customer():
    return customer_db

@app.get(
    "/customers/{customer_id}",
    response_model=Customer,
    summary="Obtener cliente por ID",
    tags=["Clientes"],
    responses={
        200: {"description": "Cliente encontrado"},
        404: {"description": "Cliente no encontrado"}
    }
)

def get_customer_by_id(customer_id: int):
    for cliente in customer_db:
        if cliente.id == customer_id:
            return cliente
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

def get_customers() -> List[Customer]:
    return customer_db
@app.post(
    "/customers",
    status_code=201,
    summary="Crear un cliente",
    description="Agregar un nuevo cliente a la base de datos simulada",
    tags=["Clientes"],
    responses={
        201: {
            "descripcion":"cliente creado exitosamente"
        },
        400: {
            "descripcion": "Id del cliente duplicado"
        }
    }
)
def crear_customer(customer: Customer) -> Customer:
    """
    Agrega un nuevo cliente a la base de datos simulada
    
    """
    for cada_cliente in customer_db:
        if cada_cliente.id == customer.id:
            raise HTTPException(status_code=400,detail="El ID ya existe")
    customer_db.append(customer)
    return customer

@app.put(
    "/customers/{customer_id}",
    response_model= Customer,
    summary="Actualizar un cliente",
    description="Se actualiza el cliente mediante su ID",
    tags=["Clientes"],
    responses={
        200: {"descripcion": "cliente actualizado correctamente"},
        404:{"descripcion": "id cliente no se encontro"}
    }
)
def actualizar_customer(customer_id: int, update_customer: Customer):
    for index, cliente_existente in enumerate(customer_db):
        if cliente_existente.id == customer_id:
            customer_db[index] = update_customer
            return update_customer
    raise HTTPException(status_code=404,detail="Cliente no encontrado")

@app.delete(
    "/customers/{customer_id}",
    summary="Eliminar un cliente",
    description="Se elimina un cliente de la base de datos por Id",
    tags=["Clientes"],
    responses={
        200: {"descripcion": "cliente eliminado correctamente"},
        404:{"descripcion": "id del cliente no encontrado"}
    }
)
def delete_customer(customer_id: int):
    for index, cliente_existente in enumerate(customer_db):
        if cliente_existente.id == customer_id:
            customer_db.pop(index)
            return {"descripcion": "cliente eliminado correctamente"}
    raise HTTPException(status_code=404,detail="Cliente no encontrado")

#Productos
products_db: List[Product] = [
    Product(id=1, name="Nintendo Switch", stock=5, price=500.0, category="Tecnologia"),
    Product(id=2, name="Castillo Barbie", stock=10, price=50.0, category="Juguetes")
]

# --- Listado de productos ---
@app.get(
    "/products",
    response_model=List[Product],
    summary="Obtener todos los productos",
    description="Esto nos devuelve una lista con todos los productos registrados",
    tags=["Productos"],
    responses={
        200: {"description": "Lista de productos recuperada exitosamente"}
    }
)
def get_all_products():
    return products_db

@app.get(
    "/products/{product_id}",
    response_model=Product,
    summary="Obtener producto por ID",
    tags=["Productos"],
    responses={
        200: {"description": "Producto encontrado"},
        404: {"description": "Producto no encontrado"}
    }
)
def get_product_by_id(product_id: int):
    for producto in products_db:
        if producto.id == product_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

def get_products() -> List[Product]:
    return products_db

@app.post(
    "/products",
    status_code=201,
    summary="Crear un producto",
    description="Agregar un nuevo producto a la base de datos simulada",
    tags=["Productos"],
    responses={
        201: {
            "descripcion":"producto creado exitosamente"
        },
        400: {
            "descripcion": "Id del producto duplicado"
        }
    }
)
def crear_product(product: Product) -> Product:
    """
    Agrega un nuevo producto a la base de datos simulada
    
    """
    for cada_producto in products_db:
        if cada_producto.id == product.id:
            raise HTTPException(status_code=400,detail="El ID ya existe")
    products_db.append(product)
    return product

@app.put(
    "/products/{product_id}",
    response_model= Product,
    summary="Actualizar un producto",
    description="Se actualiza el producto mediante su ID",
    tags=["Productos"],
    responses={
        200: {"descripcion": "producto actualizado correctamente"},
        404:{"descripcion": "id del producto no encontrado"}
    }
)
def actualizar_product(product_id: int, update_product: Product):
    for index, producto_existente in enumerate(products_db):
        if producto_existente.id == product_id:
            products_db[index] = update_product
            return update_product
    raise HTTPException(status_code=404,detail="Producto no encontrado")

@app.delete(
    "/products/{product_id}",
    summary="Eliminar un producto",
    description="Se elimina un producto de la base de datos por Id",
    tags=["Productos"],
    responses={
        200: {"descripcion": "producto eliminado correctamente"},
        404:{"descripcion": "id del producto no encontrado"}
    }
)
def delete_product(product_id: int):
    for index, producto_existente in enumerate(products_db):
        if producto_existente.id == product_id:
            products_db.pop(index)
            return {"descripcion": "producto eliminado correctamente"}
    raise HTTPException(status_code=404,detail="Producto no encontrado")

@app.get(
    "/products/filter",
    response_model=List[Product],
    summary="Filtrar productos por categoría",
    tags=["Productos"],
    responses={
        200: {"description": "Listado de productos filtrados por categoría"},
        404: {"description": "No se encontraron productos con esa categoría"}
    }
)
def filter_products(category: str | None = Query(None, description="Filtrar productos por categoría")):
    if category:
        filtered = [p for p in products_db if p.category.lower() == category.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="No se encontraron productos con esa categoría")
        return filtered
    return products_db

#Descuentos
# --- Listaao de Clientes ---
discounts_db: List[Discount] = [
    Discount(id=1, discount_percentage=0.15, flag=False),
    Discount(id=2, discount_percentage=0.15, flag=True)
]
@app.get(
    "/discounts",
    response_model=List[Discount],
    summary="Obtener todos los descuentos",
    description="Esto nos devuelve una lista con todos los descuentos registrados",
    tags=["Descuentos"],
    responses={
        200: {"description": "Lista de descuentos recuperada exitosamente"}
    }
)
def get_all_discounts():
    return discounts_db
@app.get(
    "/discounts/{discount_id}",
    response_model=Discount,
    summary="Obtener descuento por ID",
    tags=["Descuentos"],
    responses={
        200: {"description": "Descuento encontrado"},
        404: {"description": "Descuento no encontrado"}
    }
)
def get_discount_by_id(discount_id: int):
    for descuento in discounts_db:
        if descuento.id == discount_id:
            return descuento
    raise HTTPException(status_code=404, detail="Descuento no encontrado")

def get_discounts() -> List[Discount]:
    return discounts_db
@app.post(
    "/discounts",
    status_code=201,
    summary="Crear un descuento",
    description="Agregar un nuevo descuento a la base de datos simulada",
    tags=["Descuentos"],
    responses={
        201: {
            "descripcion":"descuento creado exitosamente"
        },
        400: {
            "descripcion": "Id del descuento duplicado"
        }
    }
)
def crear_discount(discount: Discount) -> Discount:
    """
    Agrega un nuevo descuento a la base de datos simulada
    
    """
    for cada_descuento in discounts_db:
        if cada_descuento.id == discount.id:
            raise HTTPException(status_code=400,detail="El ID ya existe")
    discounts_db.append(discount)
    return discount

@app.put(
    "/discounts/{discount_id}",
    response_model= Discount,
    summary="Actualizar un descuento",
    description="Se actualiza el descuento mediante su ID",
    tags=["Descuentos"],
    responses={
        200: {"descripcion": "descuento actualizado correctamente"},
        404:{"descripcion": "id del descuento no encontrado"}
    }
)
def actualizar_discount(discount_id: int, update_discount: Discount):
    for index, descuento_existente in enumerate(discounts_db):
        if descuento_existente.id == discount_id:
            discounts_db[index] = update_discount
            return update_discount
    raise HTTPException(status_code=404,detail="Descuento no encontrado")

@app.delete(
    "/discounts/{discount_id}",
    summary="Eliminar un descuento",
    description="Se elimina un descuento de la base de datos por Id",
    tags=["Descuentos"],
    responses={
        200: {"descripcion": "descuento eliminado correctamente"},
        404:{"descripcion": "id del descuento no encontrado"}
    }
)
def delete_discount(discount_id: int):
    for index, discount_existente in enumerate(discounts_db):
        if discount_existente.id == discount_id:
            discounts_db.pop(index)
            return {"descripcion": "descuento eliminado correctamente"}
    raise HTTPException(status_code=404,detail="Descuento no encontrado")