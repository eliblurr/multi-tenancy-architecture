from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.schema import CreateSchema, DropSchema
from database import SessionLocal, engine, MetaData
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session
import schemas, crud, models

api = FastAPI(docs_url="/")

# Dependency
def get_db(request:Request):
    return request.state.db

# middleware
@api.middleware("http")
async def schema_pointer(request:Request, call_next):
    try:
        db = SessionLocal()
        if request.headers.get('tenant_identity', None):
            db.connection(execution_options={"schema_translate_map": {None: request.headers.get('tenant_identity')}})
        request.state.db = db
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

@api.post('/init_db')
def init_db():
    models.Base.metadata.create_all(bind=engine, tables=[table for table in models.Base.metadata.sorted_tables if table.schema=='public'])
    return True

# tenant
@api.post('/tenant')
async def create_tenant(payload:schemas.CreateTenant, db:Session=Depends(get_db)):
    tenant = await crud.tenant.create(payload, db)
    if tenant:
        engine.execute(CreateSchema(tenant.id))
        connection = engine.connect().execution_options(schema_translate_map={None: tenant.id,})
        models.Base.metadata.create_all(bind=connection, tables=[table for table in models.Base.metadata.sorted_tables if table.schema==None])
        return tenant
      
@api.get('/tenant')
async def read_tenants(search:str=None, value:str=None, skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    return await crud.tenant.read(db, search, value, skip, limit)

@api.get('/tenant/{id}/users')
async def read_tenant_users(id:str, search:str=None, value:str=None, skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    return await crud.tenant.read_chlid(id, db, search, value, skip, limit)

@api.delete('/tenant/{id}')
async def delete_tenant(id:str, db:Session=Depends(get_db)):
    db.connection(execution_options={"schema_translate_map": {None: id}})
    if await crud.tenant.delete(id, db):
        engine.execute(DropSchema(id, cascade=True))

# user
@api.post('/users')
async def create_user(payload:schemas.CreateUser, db:Session=Depends(get_db)):
    if not await crud.tenant.read_by_id(payload.tenant_id, db):
        raise HTTPException(status_code=404, detail='tenant not found')
    return await crud.user.create(payload, db)

@api.get('/users')
async def read_users(search:str=None, value:str=None, skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    return await crud.user.read(db, search, value, skip, limit)

@api.get('/user/{id}/items')
async def read_user_items(id:int, search:str=None, value:str=None, skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    try:
        return await crud.user.read_chlid(id, db, search, value, skip, limit)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail='provide tenant id')

@api.delete('/user/{id}')
async def delete_user(id:int, db:Session=Depends(get_db)):
    try:
        return await crud.user.delete(id, db)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail='provide tenant id')

# item
@api.post('/items')
async def create_item(payload:schemas.CreateItem, db:Session=Depends(get_db)):
    try:
        if not await crud.user.read_by_id(payload.user_id, db): # check tenant as well
            raise HTTPException(status_code=404, detail='user not found')
        return await crud.item.create(payload, db)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail='provide tenant id')

@api.get('/items')
async def read_item(search:str=None, value:str=None, skip:int=0, limit:int=100, db:Session=Depends(get_db)):
    try
        return await crud.item.read(db, search, value, skip, limit)
    except ProgrammingError:
        raise HTTPException(status_code=400, detail='provide tenant id')

''' 
    References
    create_all api - https://www.kite.com/python/docs/sqlalchemy.MetaData.create_all
    CreateSchema api - https://www.kite.com/python/docs/sqlalchemy.schema.CreateSchema or https://docs.sqlalchemy.org/en/14/core/ddl.html#sqlalchemy.schema.CreateSchema
    DropSchema api - https://docs.sqlalchemy.org/en/14/core/ddl.html#sqlalchemy.schema.DropSchema
    DB session with middleware - https://fastapi.tiangolo.com/tutorial/sql-databases/#alternative-db-session-with-middleware
    Flask example - https://github.com/Senhaji-Rhazi-Hamza/multi-tenancy-example
    Translation of Schema Names - https://docs.sqlalchemy.org/en/13/core/connections.html#translation-of-schema-names
'''