import secrets, sqlalchemy as sa
from database import engine

def gen_token():
    schemas = sa.inspect(engine).get_schema_names()
    while True: 
        token = secrets.token_hex(16) 
        if token not in schemas: 
            break
    return token