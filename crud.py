from sqlalchemy.orm import Session
from fastapi import HTTPException
import sys, models

class CRUD:
    def __init__(self, model, model_c=None):
        self.model = model
        self.model_c = model_c

    async def create(self, payload, db:Session):
        try:
            obj = self.model(**payload.dict())
            db.add(obj)
            db.commit()
            db.refresh(obj) 
            return obj   
        except:
            db.rollback()
            raise HTTPException(status_code=500, detail="{}: {}".format(sys.exc_info()[0], sys.exc_info()[1]))
        finally:
            db.close()

    async def read(self, db:Session, search:str=None, value:str=None, skip:int=0, limit:int=100):
        base = db.query(self.model)
        if search and value:
            try:
                base = base.filter(self.model.__table__.c[search].like("%" + value + "%"))
            except KeyError:
                pass
        return base.offset(skip).limit(limit).all()

    async def read_by_id(self, id, db:Session):
        return db.query(self.model).filter(self.model.id == id).first()

    async def read_chlid(self, id:int, db:Session, search:str=None, value:str=None, skip:int=0, limit:int=100):
        if self.model_c:
            base = db.query(self.model_c).join(self.model).filter(self.model.id==id)
            if search and value:
                try:
                    base = base.filter(self.model_c.__table__.c[search].like("%" + value + "%"))
                except KeyError:
                    pass
            return base.offset(skip).limit(limit).all()

    async def delete(self, id, db:Session):
        try:
            obj = await self.read_by_id(id, db)
            if obj:
                db.delete(obj)
                db.commit()
                return True
            return False
        except:
            db.rollback()
            raise HTTPException(status_code=500, detail="{}: {}".format(sys.exc_info()[0], sys.exc_info()[1]))
            

tenant = CRUD(model=models.Tenant, model_c=models.User)
user = CRUD(model=models.User, model_c=models.Item)
item = CRUD(model=models.Item, model_c=None)