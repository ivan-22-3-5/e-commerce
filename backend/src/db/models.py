from datetime import datetime, UTC
from typing import Optional, Any

from sqlalchemy import (
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Table,
    Column,
    Float,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.config import rules
from src.custom_types import OrderStatus
from src.db.db import Base
from src.schemas.item import Item

product_category_association = Table(
    "product_category_association",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    identity_provider_id: Mapped[Optional[str]] = mapped_column(
        unique=True, nullable=True
    )
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[Optional[str]] = mapped_column(
        String(rules.MAX_HASHED_PASSWORD_LENGTH), nullable=True
    )
    name: Mapped[str] = mapped_column(String(rules.MAX_USERNAME_LENGTH))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user", lazy="selectin"
    )


class TokenBase(Base):
    __abstract__ = True
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    token: Mapped[str] = mapped_column(String)


class RefreshToken(TokenBase):
    __tablename__ = "refresh_tokens"


class RecoveryToken(TokenBase):
    __tablename__ = "recovery_tokens"


class ItemBase(Base):
    __abstract__ = True
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)

    @declared_attr
    def product(cls) -> Mapped["Product"]:
        return relationship("Product", lazy="selectin", uselist=False)


class CartItem(ItemBase):
    __tablename__ = "cart_items"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    @property
    def total_price(self) -> int:
        if self.product:
            return self.product.final_price * self.quantity
        return 0


class OrderItem(ItemBase):
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    total_price: Mapped[int]


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_paid: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", lazy="selectin", cascade="all, delete-orphan"
    )

    @property
    def total_price(self) -> int:
        return sum(item.total_price for item in self.items)

    def __init__(self, user_id: int, items: list[Item], **kwargs: Any):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.items = [OrderItem(**item.model_dump()) for item in items]


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(rules.MAX_PRODUCT_TITLE_LENGTH))
    description: Mapped[str] = mapped_column(
        String(rules.MAX_PRODUCT_DESCRIPTION_LENGTH)
    )
    quantity: Mapped[int]
    full_price: Mapped[int]
    discount: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    images: Mapped[list[str]] = mapped_column(JSONB, default=list)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        lazy="selectin",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        lazy="selectin",
        secondary=product_category_association,
        back_populates="products",
    )

    @property
    def final_price(self) -> int:
        return int(self.full_price * (1 - self.discount / 100))


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(rules.MAX_CATEGORY_NAME_LENGTH), unique=True
    )

    products: Mapped[list["Product"]] = relationship(
        "Product", secondary=product_category_association, back_populates="categories"
    )


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    rating: Mapped[int]
    content: Mapped[str] = mapped_column(String(rules.MAX_REVIEW_CONTENT_LENGTH))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=False),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="reviews", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="reviews", lazy="selectin")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    amount: Mapped[float]
    currency: Mapped[str] = mapped_column(String(3))
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    intent_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
