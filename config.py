from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL:str = 'postgres://postgres@0.0.0.0:3221/mtStore'
    # os.environ.get('DATABASE_URI') or 'sqlite:///./mt_store.db'

    class Config:
        env_file = ".env"

settings = Settings()