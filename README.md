API_JUGUETERIA

DESCRIPCION GENERAL:

Esta API RESTful permite gestionar una juguetería con tres recursos principales:
Clientes (registro, consulta y gestión de clientes).
Productos (juguetes electrónicos, didácticos y coleccionables).
Descuentos (gestión de promociones aplicables a productos).

La API facilita operaciones como vender, aplicar descuentos e inventariar productos.
Es útil para administrar de manera digital el negocio de una juguetería, optimizando la organización de clientes, productos y promociones.

ARQUITECTURA/ DISEÑO:

main.py          # Código principal de la API (FastAPI)
requirements.txt # Dependencias del proyecto
README.md        # Documentación del proyectO

FastAPI: Framework principal para crear la API.
Uvicorn: Servidor ASGI para ejecutar la aplicación.
Pydantic: Para validación de datos.

REQUISITOS DE INSTALACION:
Python 3.10+
Dependencias: pip install fastapi uvicorn

INSTRUCCIONES DE EJECUCION:

Clona el repositorio:git clone https://github.com/usuario/jugueteria-api.git
cd jugueteria-api

Instala las dependencias: pip install -r requirements.txt

Ejecuta el servidor con Uvicorn: uvicorn main:app --reload

Abre en el navegador:
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

ENDPOINTS:

CLIENTES:

GET /customers → Listar todos los clientes.

GET /customers/{id} → Obtener cliente por ID.

GET /customers/filter?email=... → Filtrar clientes por correo.

POST /customers → Crear un cliente (JSON en el body).

PUT /customers/{id} → Actualizar cliente.

DELETE /customers/{id} → Eliminar cliente.

PRODUCTOS:

GET /products → Listar todos los productos.

GET /products/{id} → Obtener producto por ID.

GET /products/filter?category=... → Filtrar productos por categoría.

POST /products → Crear un producto.

PUT /products/{id} → Actualizar producto.

DELETE /products/{id} → Eliminar producto.

DESCUENTOS:

GET /discounts → Listar todos los descuentos.

GET /discounts/{id} → Obtener descuento por ID.

POST /discounts → Crear descuento.

PUT /discounts/{id} → Actualizar descuento.

DELETE /discounts/{id} → Eliminar descuento.

AUTORES / INTEGRANTES DEL GRUPO
HAMILTON JULIAN RIOS SALAZAR
MARISOL DIAZ BETANCUR

