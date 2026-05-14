from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash


db = SQLAlchemy(engine_options=dict(echo=True))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(500), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password_: Mapped[str] = mapped_column(String(500))
    fullname: Mapped[Optional[str]] = mapped_column(String(500), default=None, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(500),unique=True, default=None, nullable=True)

    reservations: Mapped[List["Reservation"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4().hex
        
    @property
    def password(self):
        raise AttributeError("Немає прав на читання паролю.")
    
    @password.setter
    def password(self, raw_password: str):
        self.password_ = generate_password_hash(raw_password)

    def is_password_verify(self, raw_password):
        return check_password_hash(self.password_, raw_password)
    

class Menu(db.Model):
    __tablename__ = "menu"

    id: Mapped[str] = mapped_column(String(500), primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(String(1000), default=None, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(default=None, nullable=True)
    ingredients: Mapped[Optional[str]] = mapped_column(String(500), default=None, nullable=True)
    price: Mapped[float] = mapped_column()
    active: Mapped[bool] = mapped_column(Boolean(), default=True)
    picture: Mapped[Optional[str]] = mapped_column(String(500), default=None, nullable=True)

    orders_items: Mapped[List["OrderItem"]] = relationship(back_populates="menu_item")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4().hex


class Reservation(db.Model):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(String(500), primary_key=True)
    time_start: Mapped[datetime] = mapped_column(DateTime())
    table: Mapped[Optional[str]] = mapped_column(String(100), default=None, nullable=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="reservations")
    order: Mapped[List["Order"]] = relationship(back_populates="reservation")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4().hex


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id: Mapped[str] = mapped_column(String(500), primary_key=True)
    menu_id: Mapped[str] = mapped_column(ForeignKey(Menu.id, ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(default=1)

    menu_item: Mapped[Menu] = relationship(back_populates="order_items")
    order: Mapped["Order"] = relationship(back_populates="order_items")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4().hex


class Order(db.Model):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(500), primary_key=True)
    order_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    reservation_id: Mapped[str] = mapped_column(ForeignKey(Reservation.id, ondelete="CASCADE"))

    order_items: Mapped[List[OrderItem]] = relationship(back_populates="order")
    user: Mapped[User] = relationship(back_populates="orders")
    reservation: Mapped[Reservation] = relationship(back_populates="order")
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4().hex        
