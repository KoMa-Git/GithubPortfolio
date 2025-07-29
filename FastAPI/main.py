from typing import Union, Optional, Annotated
from fastapi import FastAPI, Path, Query, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from pydantic import BaseModel
from scrape import *
from sql import *

# add table to the database
class users(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    name : str = Field(index=True)
    email : str

class employee(SQLModel, table=True):
    employee_id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(index=True)
    age: int
    position: str

# add multiple models for separate purpose, create or send public, etc.
class create_employee(SQLModel):
    full_name: str
    age: int
    position: str

class public_employee(SQLModel):
    employee_id: int
    full_name: str
    position: str

class update_employee(SQLModel):
    full_name: str | None = None
    age: int | None = None
    position: str | None = None

# add database connection url
postgresql_url = os.environ['POSTGRESQL_URI']

#start engine
engine = create_engine(postgresql_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# can be only one session at each interact, this solution use separate function and reference, other way is to use "with session" in each functions
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# need to build db and tables if not already built you can do it with lifespan
@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    # code before yield runs before webserver start
    yield

# start the app
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/calculate")
def get_result_query(x: float, y: float, operator: str = Query(None, title="Operator", description="It could be plus/minus/multiply/divide")):
    if operator == "plus":
        return {"Result": x+y}
    elif operator == "minus":
        return {"Result": x-y}
    elif operator == "multiply":
        return {"Result": x*y}
    elif operator == "divide":
        if y == 0:
            raise HTTPException(status_code=400, detail="Division by zero")
        else:
            return {"Result": x/y}
    else:
        return{"Error":"Please missing or mistyped values or operator"}

@app.get("/calculate/{x}-{operator}-{y}")
def get_result_path(x: int, y: int, operator: str = Path(description="It could be plus/minus/multiply/divide")):
    if operator == "plus":
        return {"Result": x+y}
    elif operator == "minus":
        return {"Result": x-y}
    elif operator == "multiply":
        return {"Result": x*y}
    elif operator == "divide":
        if y == 0:
            raise HTTPException(status_code=400, detail="Division by zero")
        else:
            return {"Result": x/y}
    else:
        return{"Error":"Please missing or mistyped values or operator"}

# this is using a function from an another file, little webscrape demo  
@app.get("/get-a-quote")
def get_a_quote():
    return random_quote()

# Following imported functions are little SQL demo through a freely deployed PostrgerSQL on render.com uses psycopg2
@app.get("/read_database")
def read_sql_db():
    return read_data()

@app.post("/insert_into_database")
def insert_into_sql_db(name: str = Query(None, title="Name", description="Add the new employee name"),
                  age: int = Query(None, title="Age", description="Add the age of the new employee"),
                  position: str = Query(None, title="position", description="Add the position of the new employee")):
    return insert_data(name,age,position)

@app.post("/delete_from_database")
def delete_from_sql_db(id: int = Query(None, title="ID", description="Add the id of the employee")):
    return delete_data(id)

# Following uses sqlmodel more clear version of db handling

@app.get("/view")
def read_it(session: SessionDep): #-> list[users]:
    usrs = session.exec(select(employee)).all()
    return usrs

@app.post("/employee", response_model=public_employee)
def add_employee(emp: create_employee, session: SessionDep):
    db_emp = employee.model_validate(emp)
    session.add(db_emp)
    session.commit()
    session.refresh(db_emp)
    return db_emp

@app.patch("/employee/{id}", response_model=public_employee)
def udt_employee(id, emp:update_employee, session: SessionDep):
    db_emp = session.get(employee, id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="employee not found")
    emp_data = emp.model_dump(exclude_unset=True)
    db_emp.sqlmodel_update(emp_data)
    session.add(db_emp)
    session.commit()
    session.refresh(db_emp)
    return db_emp

@app.delete("/employee/{id}")
def del_employee(id, session: SessionDep):
    emp = session.get(employee, id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(emp)
    session.commit()
    return { "ok": True}
