import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read DATABASE_URL from environment variable
# Same as reading spring.datasource.url from application.properties
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_db")

# create_engine = DataSource in Spring Boot
# This creates the actual connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# sessionmaker = EntityManagerFactory in Spring Boot
# Every database operation needs a session (like a transaction context)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
# Same as @Entity base in JPA — all your table models extend this
Base = declarative_base()


# Dependency function — used by FastAPI endpoints
# Same as @Autowired EntityManager in Spring Boot
# yields a session, closes it automatically when request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()