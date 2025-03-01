from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  # Import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session
from app.core.config import settings

# Create the Base class using declarative_base
Base = declarative_base()  # This is the Base class that models should inherit from

# Create the database engine using SQLModel's engine
engine = create_engine(str(settings.database_url), echo=True)

# Dependency to get a new database session for each request
def get_session():
    with Session(engine) as session:  # Using SQLModel's Session here
        yield session

print(Base.metadata)