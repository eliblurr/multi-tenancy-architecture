from pydantic import BaseModel

class CreateTenant(BaseModel):
    title:str

class Tenant(BaseModel):
    id:int
    title:str

    class Config:
        orm_mode=True

class CreateUser(BaseModel):
    email:str
    tenant_id:str

class User(BaseModel):
    id: int
    email:str
    tenant:Tenant # disposable

    class Config:
        orm_mode=True

class CreateItem(BaseModel):
    title:str
    user_id:int
    description:str

class Item(BaseModel):
    id:int
    user:User # disposable
    title:str
    description:str

    class Config:
        orm_mode = True