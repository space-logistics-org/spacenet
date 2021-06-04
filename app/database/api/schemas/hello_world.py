from pydantic import BaseModel

from spacenet.schemas import hello_world as schemas

class HelloWorldCreate(schemas.HelloWorld):
    pass

class HelloWorld(schemas.HelloWorld):
    id: int
    class Config:
        orm_mode = True
