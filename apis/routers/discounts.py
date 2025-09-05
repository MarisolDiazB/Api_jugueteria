from fastapi import APIRouter, HTTPException
from typing import List
from models import Discount
from db import discounts_db, products_db

router = APIRouter(
    prefix="/discounts",
    tags=["Descuentos"]
)

@router.get("", response_model=List[Discount])
def get_all_discounts():
    return discounts_db

@router.get("/{discount_id}", response_model=Discount)
def get_discount_by_id(discount_id: int):
    for descuento in discounts_db:
        if descuento.id == discount_id:
            return descuento
    raise HTTPException(status_code=404, detail="Descuento no encontrado")

@router.post("", status_code=201, response_model=Discount)
def crear_discount(discount: Discount):
    for d in discounts_db:
        if d.id == discount.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
    if not any(p.id == discount.id_product for p in products_db):
        raise HTTPException(status_code=400, detail="El producto no existe")
    discounts_db.append(discount)
    return discount

@router.put("/{discount_id}", response_model=Discount)
def actualizar_discount(discount_id: int, update_discount: Discount):
    for index, descuento_existente in enumerate(discounts_db):
        if descuento_existente.id == discount_id:
            # 🔒 Blindar ID
            if update_discount.id != descuento_existente.id:
                raise HTTPException(status_code=400, detail="El ID no se puede modificar")
            if not any(p.id == update_discount.id_product for p in products_db):
                raise HTTPException(status_code=400, detail="El producto no existe")
            discounts_db[index] = update_discount
            return update_discount
    raise HTTPException(status_code=404, detail="Descuento no encontrado")

@router.delete("/{discount_id}")
def delete_discount(discount_id: int):
    for index, descuento_existente in enumerate(discounts_db):
        if descuento_existente.id == discount_id:
            discounts_db.pop(index)
            return {"description": "descuento eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Descuento no encontrado")
