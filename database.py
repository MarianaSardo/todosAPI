from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

'''import os


DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

'''

SQLALCHEMY_DATABASE_URL = "postgresql://tvbbeiof:Q874-EKT6qC7HWqXZb0GbC862OBIvX76@motty.db.elephantsql.com/tvbbeiof"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
