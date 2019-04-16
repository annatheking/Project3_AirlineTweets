from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
import os

# Create Dog and Cat Classes
# ----------------------------------
class Tweet(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email= Column(String(30))
    phone=Column(String(30))
    

