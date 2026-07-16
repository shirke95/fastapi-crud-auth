from sqlalchemy import Column, Integer, String
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)


class Tutorial(Base):
    __tablename__ = "tutorials"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    author = Column(String)
    description = Column(String)
