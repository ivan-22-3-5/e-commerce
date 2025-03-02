from datetime import datetime, UTC

from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey, Float, Boolean, Enum, Table, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.custom_types import OrderStatus
from src.db.db import Base

product_category_association = Table(
    'product_category_association', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('category_name', String, ForeignKey('categories.name'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC),
                                                 nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    reviews: Mapped[list["Review"]] = relationship('Review')


class Address(Base):
    __tablename__ = 'addresses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    fullname: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    street: Mapped[str] = mapped_column(String, nullable=False)
    zipcode: Mapped[str] = mapped_column(String, nullable=False)


class TokenBase(Base):
    __abstract__ = True
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    token: Mapped[str] = mapped_column(String, nullable=False)


class RefreshToken(TokenBase):
    __tablename__ = 'refresh_tokens'


class RecoveryToken(TokenBase):
    __tablename__ = 'recovery_tokens'


class ConfirmationToken(TokenBase):
    __tablename__ = 'confirmation_tokens'


class ItemBase(Base):
    __abstract__ = True
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    @declared_attr
    def product(cls) -> Mapped["Product"]:
        return relationship('Product', lazy="selectin", uselist=False)

    @hybrid_property
    def total_price(self):
        return self.product.final_price * self.quantity


class CartItem(ItemBase):
    __tablename__ = 'cart_items'
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey('carts.id'), primary_key=True)


class Cart(Base):
    __tablename__ = 'carts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    items: Mapped[list["CartItem"]] = relationship('CartItem', lazy="selectin", cascade="all, delete-orphan")

    @hybrid_property
    def total_price(self):
        return sum(item.total_price for item in self.items)

    def add_item(self, product_id: int, quantity: int):
        existing_item = next((item for item in self.items if item.product_id == product_id), None)
        if existing_item:
            existing_item.quantity += quantity
        else:
            self.items.append(CartItem(product_id=product_id, quantity=quantity))

    def remove_item(self, product_id: int, quantity: int):
        existing_item = next((item for item in self.items if item.product_id == product_id), None)
        if existing_item:
            if existing_item.quantity <= quantity:
                self.items.remove(existing_item)
            else:
                existing_item.quantity -= quantity

    def clear(self):
        self.items = []


class OrderItem(ItemBase):
    __tablename__ = 'order_items'
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), primary_key=True)


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC),
                                                 nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey('addresses.id'))
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    address: Mapped["Address"] = relationship('Address', uselist=False)
    items: Mapped[list["OrderItem"]] = relationship('OrderItem', lazy='selectin')

    @hybrid_property
    def total_price(self):
        return sum(item.total_price for item in self.items)

    def __init__(self, user_id: int, address_id: int, items: list[dict[str, int]]):
        super().__init__()
        self.user_id = user_id
        self.address_id = address_id
        self.items = [OrderItem(**item) for item in items]


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    full_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC),
                                                 nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categories: Mapped[list["Category"]] = relationship('Category',
                                                        back_populates='products',
                                                        lazy='selectin',
                                                        secondary=product_category_association)
    reviews: Mapped[list["Review"]] = relationship('Review', lazy='selectin')

    @hybrid_property
    def rating(self):
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1) if self.reviews else 0

    @hybrid_property
    def final_price(self):
        return round(self.full_price * (1 - self.discount / 100), 2)


class Category(Base):
    __tablename__ = 'categories'
    name: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC),
                                                 nullable=False)

    products: Mapped[list["Product"]] = relationship('Product', back_populates='categories', lazy="selectin",
                                                     secondary=product_category_association)


class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC),
                                                 nullable=False)


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    payment_method = Column(String, nullable=False)
    intent_id = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC))
