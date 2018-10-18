import sys
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

class courseDetails(Base):
    __tablename__ = 'course_details'

    id = Column(Integer, primary_key=True)
    filepath = Column(String(350), nullable=False)
    filename = Column(String(350), nullable=False)
    coursetitle = Column(String(350), nullable=False)
    coursecode = Column(String(350), nullable=False)
    category = Column(String(350), nullable=False)
    year = Column(Integer)

engine = create_engine('sqlite:///filedetails.db')
Base.metadata.create_all(engine)