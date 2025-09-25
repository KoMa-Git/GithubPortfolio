from typing import Optional, List
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from passlib.context import CryptContext
from jose import JWTError, jwt

# ----------------------
# Configuration
# ----------------------
DATABASE_URL = "sqlite:///:memory:"
JWT_SECRET = os.getenv("JWT_SECRET") or "super-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

#engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else None)
engine = create_engine("sqlite:///database.db", echo=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# ----------------------
# Models
# ----------------------
class UserBase(SQLModel):
    username: str = Field(index=True)
    email: EmailStr = Field(index=True)
    is_admin: bool = False

class User(UserBase, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    lends: List["Lend"] = Relationship(back_populates="user")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

class BookBase(SQLModel):
    title: str
    author: Optional[str] = None

class Book(BookBase, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    copies_total: int = 1
    copies_available: int = 1
    lends: List["Lend"] = Relationship(back_populates="book")

class BookCreate(BaseModel):
    title: str
    author: Optional[str] = None
    copies: int = 1

class BookRead(BaseModel):
    id: int
    title: str
    author: Optional[str]
    copies_total: int
    copies_available: int

class Lend(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    lend_start: datetime = Field(default_factory=datetime.utcnow)
    lend_end: Optional[datetime] = None
    returned: bool = False

    user: Optional[User] = Relationship(back_populates="lends")
    book: Optional[Book] = Relationship(back_populates="lends")

class LendRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    lend_start: datetime
    lend_end: Optional[datetime]
    returned: bool

# ----------------------
# Utility functions
# ----------------------

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


def admin_required(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# ----------------------
# Lifespan: startup with seed
# ----------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup tasks
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(User)).first()
        if not existing:
            admin = User(username="admin", email="admin@example.com", hashed_password=get_password_hash("adminpass"), is_admin=True)
            user = User(username="alice", email="alice@example.com", hashed_password=get_password_hash("alicepass"), is_admin=False)
            b1 = Book(title="1984", author="George Orwell", copies_total=2, copies_available=2)
            b2 = Book(title="The Hobbit", author="J.R.R. Tolkien", copies_total=1, copies_available=1)
            session.add_all([admin, user, b1, b2])
            session.commit()

    yield  # Application runs here

app = FastAPI(title="Library API", lifespan=lifespan)

# ----------------------
# Endpoints
# ----------------------

@app.get("/status")
def status():
    return {"status": "ok"}

# Register
@app.post("/register", response_model=UserRead)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where((User.username == user_in.username) | (User.email == user_in.email))).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = User(username=user_in.username, email=user_in.email, hashed_password=get_password_hash(user_in.password), is_admin=False)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead(id=user.id, username=user.username, email=user.email, is_admin=user.is_admin)

# Token (login)
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Books list
@app.get("/books", response_model=List[BookRead])
def list_books(session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    return [BookRead(id=b.id, title=b.title, author=b.author, copies_total=b.copies_total, copies_available=b.copies_available) for b in books]

# Add book (admin)
@app.post("/books", response_model=BookRead)
def add_book(book_in: BookCreate, admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    book = Book(title=book_in.title, author=book_in.author, copies_total=book_in.copies, copies_available=book_in.copies)
    session.add(book)
    session.commit()
    session.refresh(book)
    return BookRead(id=book.id, title=book.title, author=book.author, copies_total=book.copies_total, copies_available=book.copies_available)

# Update book (admin)
@app.put("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, book_in: BookCreate, admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    # adjust available based on change in total
    diff = book_in.copies - book.copies_total
    book.title = book_in.title
    book.author = book_in.author
    book.copies_total = book_in.copies
    book.copies_available = max(0, book.copies_available + diff)
    session.add(book)
    session.commit()
    session.refresh(book)
    return BookRead(id=book.id, title=book.title, author=book.author, copies_total=book.copies_total, copies_available=book.copies_available)

# Delete book (admin)
@app.delete("/books/{book_id}")
def delete_book(book_id: int, admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    # optional: prevent deletion if lent out
    active = session.exec(select(Lend).where((Lend.book_id == book_id) & (Lend.returned == False))).first()
    if active:
        raise HTTPException(status_code=400, detail="Cannot delete book while it has active lends")
    session.delete(book)
    session.commit()
    return {"detail": "deleted"}

# Lend (auth required)
@app.post("/lend")
def lend_book(book_id: int = Body(..., embed=True), current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.copies_available < 1:
        raise HTTPException(status_code=400, detail="No copies available")
    # create lend
    lend = Lend(user_id=current_user.id, book_id=book_id)
    book.copies_available -= 1
    session.add(lend)
    session.add(book)
    session.commit()
    session.refresh(lend)
    return {"detail": "lent", "lend_id": lend.id}

# Giveback
@app.post("/giveback")
def giveback(lend_id: int = Body(..., embed=True), current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    lend = session.get(Lend, lend_id)
    if not lend:
        raise HTTPException(status_code=404, detail="Lend record not found")
    if lend.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed to return this lend")
    if lend.returned:
        raise HTTPException(status_code=400, detail="Already returned")
    lend.returned = True
    lend.lend_end = datetime.utcnow()
    book = session.get(Book, lend.book_id)
    if book:
        book.copies_available += 1
        session.add(book)
    session.add(lend)
    session.commit()
    return {"detail": "returned"}

# My books
@app.get("/mybooks", response_model=List[LendRead])
def mybooks(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    lends = session.exec(select(Lend).where((Lend.user_id == current_user.id) & (Lend.returned == False))).all()
    return [LendRead(id=l.id, user_id=l.user_id, book_id=l.book_id, lend_start=l.lend_start, lend_end=l.lend_end, returned=l.returned) for l in lends]

# Admin books list (with history)
@app.get("/admin/books")
def admin_books_list(admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    books = session.exec(select(Book)).all()
    result = []
    for b in books:
        history = session.exec(select(Lend).where(Lend.book_id == b.id)).all()
        hist_list = []
        for h in history:
            u = session.get(User, h.user_id)
            hist_list.append({
                "username": u.username if u else None,
                "email": u.email if u else None,
                "lend_start": h.lend_start,
                "lend_end": h.lend_end,
                "returned": h.returned,
            })
        result.append({
            "book": {"id": b.id, "title": b.title, "author": b.author, "copies_total": b.copies_total, "copies_available": b.copies_available},
            "history": hist_list,
        })
    return result

# Admin book history
@app.get("/admin/books/{book_id}/history")
def admin_book_history(book_id: int, admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    history = session.exec(select(Lend).where(Lend.book_id == book_id)).all()
    out = []
    for h in history:
        u = session.get(User, h.user_id)
        out.append({"lend_id": h.id, "username": u.username if u else None, "email": u.email if u else None, "lend_start": h.lend_start, "lend_end": h.lend_end, "returned": h.returned})
    return {"book": {"id": book.id, "title": book.title}, "history": out}

# Admin users list
@app.get("/admin/users")
def admin_users_list(admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    out = []
    for u in users:
        active_count = session.exec(select(Lend).where((Lend.user_id == u.id) & (Lend.returned == False))).count()
        history = session.exec(select(Lend).where(Lend.user_id == u.id)).all()
        hist_list = []
        for h in history:
            b = session.get(Book, h.book_id)
            hist_list.append({"book_title": b.title if b else None, "lend_start": h.lend_start, "lend_end": h.lend_end, "returned": h.returned})
        out.append({"user": {"id": u.id, "username": u.username, "email": u.email, "is_admin": u.is_admin}, "active_lend_count": active_count, "history": hist_list})
    return out

# Admin user history
@app.get("/admin/users/{user_id}/history")
def admin_user_history(user_id: int, admin: User = Depends(admin_required), session: Session = Depends(get_session)):
    u = session.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    history = session.exec(select(Lend).where(Lend.user_id == user_id)).all()
    out = []
    for h in history:
        b = session.get(Book, h.book_id)
        out.append({"lend_id": h.id, "book_title": b.title if b else None, "lend_start": h.lend_start, "lend_end": h.lend_end, "returned": h.returned})
    return {"user": {"id": u.id, "username": u.username, "email": u.email}, "history": out}

# Run guard
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
