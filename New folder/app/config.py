from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL='postgres://postgres:123@localhost:5432/Online_shopping'

engine = create_engine(DATABASE_URL, dialect='postgresql',
                       pool_size=20, max_overflow=0,
                       echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind=engine)
Base = declarative_base()
