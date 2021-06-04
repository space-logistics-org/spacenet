from typing import List
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from .. import database
from ..models import hello_world as models
from ..schemas import hello_world as schemas

# build a new router
router = APIRouter()

# bind a route to list objects
@router.get("/", response_model=List[schemas.HelloWorld])
def list_hellos(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    db_hellos = db.query(models.HelloWorld).offset(skip).limit(limit).all()
    return db_hellos

# bind a route to read an object by id
@router.get("/{id}", response_model=schemas.HelloWorld)
def read_hello(id: int, db: Session = Depends(database.get_db)):
    db_hello = db.query(models.HelloWorld).get(id)
    if db_hello is None:
        raise HTTPException(status_code=404, detail="Hello not found")
    return db_hello

# bind a route to create a new object
@router.post("/", response_model=schemas.HelloWorld)
def create_hello(hello: schemas.HelloWorldCreate, db: Session = Depends(database.get_db)):
    db_hello = models.HelloWorld(**hello.dict())
    db.add(db_hello)
    db.commit()
    db.refresh(db_hello)
    return db_hello

# bind a route to update an object by id
@router.put("/{id}", response_model=schemas.HelloWorld)
def update_hello(id: int, hello: schemas.HelloWorldCreate, db: Session = Depends(database.get_db)):
    db_hello = db.query(models.HelloWorld).get(id)
    if db_hello is None:
        raise HTTPException(status_code=404, detail="Hello not found")
    for field in hello.dict():
        if hasattr(db_hello, field):
            setattr(db_hello, field, hello.dict()[field])
    db.commit()
    return db_hello

# bind a route to delete an object by id
@router.delete("/{id}", response_model=schemas.HelloWorld)
def delete_hello(id: int, db: Session = Depends(database.get_db)):
    db_hello = db.query(models.HelloWorld).get(id)
    if db_hello is None:
        raise HTTPException(status_code=404, detail="Hello not found")
    db.delete(db_hello)
    db.commit()
    return db_hello
