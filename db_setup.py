import sys
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os

Base = declarative_base()

class courseDetails(Base):
    __tablename__ = 'course_details'

    id = Column(Integer, primary_key=True)
    filepath = Column(String(350), nullable=False)
    filename = Column(String(350), nullable=False)
    coursetitle = Column(String(350), nullable=False)
    coursecode = Column(String(7), nullable=False)
    category = Column(String(350), nullable=False)
    year = Column(String(8))
    
engine = create_engine(os.environ['DATABASE_URL'])
Base.metadata.create_all(engine)