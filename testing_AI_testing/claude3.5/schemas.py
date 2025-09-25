from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

# Book schemas
class BookShort(BaseModel):
    title: str
    author: str
    isbn: str

    class Config:
        from_attributes = True    

class BookBase(BookShort):
    quantity: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    quantity: Optional[int] = None

class Book(BookBase):
    id: int
    available: int

    class Config:
        from_attributes = True

# Lend schemas
class LendBase(BaseModel):
    book_id: int

class LendCreate(LendBase):
    pass

class LendHistory(BaseModel):
    id: int
    lender_name: str
    lend_date: datetime
    return_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class Lend(BaseModel):
    id: int
    lend_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool
    book: BookShort

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Admin specific schemas
class BookHistory(BaseModel):
    lender_name: str
    lend_date: datetime
    return_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminBookView(Book):
    history: List[BookHistory]

class UserHistory(User):
    user_active_lends: int
    lends: List[Lend]

    class Config:
        from_attributes = True

# Status schema
class Status(BaseModel):
    status: str
    timestamp: datetime