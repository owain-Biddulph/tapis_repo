import random as rand
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()

class Transactions(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key = True)
    product = Column(String(250))
    buyer = Column(String(250))
    seller = Column(String(250))
    time = Column(String(250))
    quantity = Column(Integer, default = 'NA')

engine = create_engine('sqlite:///tapis_create_db.db')

Base.metadata.create_all(engine)

