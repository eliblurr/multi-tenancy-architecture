from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime, utils

class BaseMixin(object):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Tenant(BaseMixin, Base):
    __tablename__ = 'tenants'
    __table_args__ = ({'schema':'public'},)

    title = Column(String, nullable=False, unique=True)
    users = relationship('User', backref='tenant', uselist=True, cascade='all, delete')
    id = Column(String, primary_key=True, nullable=False, unique=True, default=utils.gen_token)

class User(BaseMixin, Base):
    __tablename__ = 'users'
    __table_args__ = ({'schema':'public'},)

    email = Column(String, nullable=False, unique=True)
    items = relationship('Item', backref='user', uselist=True, cascade='all, delete')
    tenant_id = Column(String, ForeignKey('public.tenants.id'), nullable=False)

class Item(BaseMixin, Base):
    __tablename__ = 'items'

    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('public.users.id'), nullable=False)