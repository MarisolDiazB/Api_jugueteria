from fastapi import APIRouter, HTTPException, Query
from typing import List
from models import Customer
from db import customer_db

router = APIRouter(
    prefix="/customers",
    tags=["Clientes"]
)

@router.get("", response_model=List[Customer])
def get_all_customer():
    return customer_db

@router.get("/filter", response_model=List[Customer])
def filter_customers(email: str | None = Query(None)):
    if email:
        filtered = [c for c in customer_db if c.email.lower() == email.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="No se encontraron clientes con ese correo")
        return filtered
    return customer_db

@router.get("/{customer_id}", response_model=Customer)
def get_customer_by_id(customer_id: int):
    for cliente in customer_db:
        if cliente.id == customer_id:
            return cliente
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@router.post("", status_code=201, response_model=Customer)
def crear_customer(customer: Customer):
    for c in customer_db:
        if c.id == customer.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
        if c.email.lower() == customer.email.lower():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
    customer_db.append(customer)
    return customer

@router.put("/{customer_id}", response_model=Customer)
def actualizar_customer(customer_id: int, update_customer: Customer):
    for index, cliente_existente in enumerate(customer_db):
        if cliente_existente.id == customer_id:
            # 🔒 Blindar ID
            if update_customer.id != cliente_existente.id:
                raise HTTPException(status_code=400, detail="El ID no se puede modificar")
            customer_db[index] = update_customer
            return update_customer
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@router.delete("/{customer_id}")
def delete_customer(customer_id: int):
    for index, cliente_existente in enumerate(customer_db):
        if cliente_existente.id == customer_id:
            customer_db.pop(index)
            return {"description": "cliente eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Cliente no encontrado")
