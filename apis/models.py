"""Modelos ORM de SQLAlchemy para la API de Juguetería.

Todas las entidades usan UUID como clave primaria y heredan columnas
de auditoría mediante AuditMixin. Las relaciones reflejan el dominio
básico de categorías, proveedores, productos, clientes, pedidos y descuentos.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class AuditMixin:
    """Campos de autoría estándar presentes en todas las entidades."""

    creado_por: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    actualizado_por: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.sysdatetime()
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.sysdatetime(), onupdate=func.sysdatetime()
    )


class User(Base, AuditMixin):
    """Usuario del sistema con credenciales y estado de actividad."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Category(Base, AuditMixin):
    """Clasificación de productos para organización y filtrado."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    products: Mapped[List["Product"]] = relationship(
        back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )


class Supplier(Base, AuditMixin):
    """Proveedor de productos con datos de contacto."""

    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    contact_info: Mapped[str] = mapped_column(String(255), nullable=True)

    products: Mapped[List["Product"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan", passive_deletes=True
    )


class Product(Base, AuditMixin):
    """Producto disponible para venta con existencias, precio y relaciones."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    category_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )

    category: Mapped["Category"] = relationship(back_populates="products")
    supplier: Mapped["Supplier"] = relationship(back_populates="products")
    discounts: Mapped[List["Discount"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", passive_deletes=True
    )


class Customer(Base, AuditMixin):
    """Cliente con nombre y correo único para compras y pedidos."""

    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)


class Discount(Base, AuditMixin):
    """Descuento asociado a un producto con porcentaje y estado."""

    __tablename__ = "discounts"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER, ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    discount_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    product: Mapped["Product"] = relationship(back_populates="discounts")


class Order(Base, AuditMixin):
    """Pedido de un cliente con estado y total acumulado."""

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER, ForeignKey("customers.id", ondelete="NO ACTION"), index=True, nullable=False
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.sysdatetime()
    )
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pendiente")

    customer: Mapped["Customer"] = relationship()
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )


class OrderItem(Base, AuditMixin):
    """Detalle de un pedido con producto, cantidad y precio unitario."""

    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER, ForeignKey("products.id", ondelete="NO ACTION"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
