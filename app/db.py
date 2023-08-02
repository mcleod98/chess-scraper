from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from models import Base


def get_session(config):
    """Provides a connection to the database through sqlalchemy session"""
    engine= create_engine(config.postgres_dsn(), echo=False)
    Session = sessionmaker(engine, expire_on_commit=True)
    return Session()

def initialize_db_tool(config):
    globalbase = Base
    engine= create_engine(config.postgres_dsn(), echo=False)
    globalbase.metadata.bind = engine
    globalbase.metadata.drop_all()
    globalbase.metadata.create_all()