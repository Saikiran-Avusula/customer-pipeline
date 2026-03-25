from sqlalchemy import Column, String, Text, Date, DECIMAL, TIMESTAMP
from database import Base

# @Entity in Spring Boot = class that extends Base here
# @Table(name="customers") = __tablename__
class Customer(Base):
    __tablename__ = "customers"

    # @Id @Column in Spring Boot = Column() with primary_key=True here
    customer_id    = Column(String(50),  primary_key=True, index=True)
    first_name     = Column(String(100), nullable=False)
    last_name      = Column(String(100), nullable=False)
    email          = Column(String(255), nullable=False)
    phone          = Column(String(20),  nullable=True)
    address        = Column(Text,        nullable=True)
    date_of_birth  = Column(Date,        nullable=True)
    account_balance= Column(DECIMAL(15, 2), nullable=True)
    created_at     = Column(TIMESTAMP,   nullable=True)