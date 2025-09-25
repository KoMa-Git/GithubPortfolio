from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    lends = relationship("Lend", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=1)
    available = Column(Integer)

    # Relationships
    lends = relationship("Lend", back_populates="book")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available = self.quantity

class Lend(Base):
    __tablename__ = "lends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    lend_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    is_returned = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="lends")
    book = relationship("Book", back_populates="lends")