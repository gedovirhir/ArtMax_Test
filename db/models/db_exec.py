from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine

import psycopg2
import os



db_name = os.getenv('POSTGRES_DB')
user_name = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')

engine = create_engine(f'postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{db_name}', isolation_level="AUTOCOMMIT")
session = sessionmaker(bind=engine)

base = declarative_base()


def create_db():
    base.metadata.create_all(engine)