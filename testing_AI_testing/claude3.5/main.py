from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models, schemas, auth
from database import engine, get_db
from typing import List

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library API")

# Initialize admin and sample data
def init_db(db: Session):
    # Create admin user if not exists
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        admin = models.User(
            email="admin@library.com",
            username="admin",
            hashed_password=auth.get_password_hash("admin123"),
            is_admin=True
        )
        db.add(admin)
        
        # Create sample user
        user = models.User(
            email="user@example.com",
            username="testuser",
            hashed_password=auth.get_password_hash("user123"),
            is_admin=False
        )
        db.add(user)
        
        # Add sample books
        books = [
            models.Book(title="1984", author="George Orwell", isbn="978-0451524935", quantity=3),
            models.Book(title="The Hobbit", author="J.R.R. Tolkien", isbn="978-0547928227", quantity=2),
            models.Book(title="Pride and Prejudice", author="Jane Austen", isbn="978-0141439518", quantity=4)
        ]
        for book in books:
            db.add(book)
        
        db.commit()

# Basic status endpoint
@app.get("/status", response_model=schemas.Status)
def get_status():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Auth endpoints
@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Book endpoints
@app.get("/books", response_model=List[schemas.Book])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@app.post("/books", response_model=schemas.Book)
def add_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int,
    book: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted"}

# Lending endpoints
@app.post("/lend/{book_id}", response_model=schemas.Lend)
def lend_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.available <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    
    lend = models.Lend(
        user_id=current_user.id,
        book_id=book_id
    )
    book.available -= 1
    
    db.add(lend)
    db.commit()
    db.refresh(lend)
    return lend

@app.post("/return/{lend_id}")
def return_book(
    lend_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    lend = db.query(models.Lend).filter(
        models.Lend.id == lend_id,
        models.Lend.user_id == current_user.id,
        models.Lend.is_returned == False
    ).first()
    
    if not lend:
        raise HTTPException(status_code=404, detail="Lend record not found")
    
    lend.is_returned = True
    lend.return_date = datetime.utcnow()
    lend.book.available += 1
    
    db.commit()
    return {"detail": "Book returned successfully"}

@app.get("/mybooks", response_model=List[schemas.Lend])
def get_my_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    lends = db.query(models.Lend).filter(
        models.Lend.user_id == current_user.id,
        models.Lend.is_returned == False
    ).all()

    return [schemas.Lend(
        id = lend.id,
        lend_date=lend.lend_date,
        return_date=lend.return_date,
        is_returned=lend.is_returned,
        book=lend.book
    ) for lend in lends]

# Admin endpoints
@app.get("/admin/books", response_model=List[schemas.AdminBookView])
def admin_books_list(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    books = db.query(models.Book).all()
    result = []

    for book in books:
        admin_view = schemas.AdminBookView(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            quantity=book.quantity,
            available=book.available,
            history=[]
        )

        for lend in book.lends:
            history_entry= schemas.BookHistory(
                lender_name=lend.user.username,
                lend_date=lend.lend_date,
                return_date=lend.return_date
            )
            admin_view.history.append(history_entry)
        
        result.append(admin_view)

    return result
    
@app.get("/admin/books/{book_id}/history", response_model=schemas.AdminBookView)
def admin_book_history(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    admin_view = schemas.AdminBookView(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        quantity=book.quantity,
        available=book.available,
        history=[]
    )

    for lend in book.lends:
        history_entry= schemas.BookHistory(
            lender_name=lend.user.username,
            lend_date=lend.lend_date,
            return_date=lend.return_date
        )
        admin_view.history.append(history_entry)

    return admin_view

@app.get("/admin/users", response_model=List[schemas.UserHistory])
def admin_users_list(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    users = db.query(models.User).all()
    result = []

    for user in users:
        user_active_lends = db.query(models.Lend).filter(models.Lend.user_id == user.id, models.Lend.is_returned == False).count()
        lends = db.query(models.Lend).filter(models.Lend.user_id == user.id).all()
        user_records = schemas.UserHistory(
            id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            user_active_lends=user_active_lends,
            lends=lends
        )
        result.append(user_records)
    
    return result

@app.get("/admin/users/{user_id}/history", response_model=schemas.UserHistory)
def admin_user_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.is_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_active_lends = db.query(models.Lend).filter(models.Lend.user_id == user_id, models.Lend.is_returned == False).count() 
    lends = db.query(models.Lend).filter(models.Lend.user_id == user_id).all()

    return schemas.UserHistory(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        user_active_lends=user_active_lends,
        lends=lends
    )

# Initialize database with sample data
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    init_db(db)