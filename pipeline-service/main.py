from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models.customer import Customer
from services.ingestion import fetch_all_customers_from_flask, upsert_customers

# Create all tables in PostgreSQL on startup
# Same as spring.jpa.hibernate.ddl-auto=update in Spring Boot
Base.metadata.create_all(bind=engine)

# FastAPI app — same as @SpringBootApplication
app = FastAPI(title="Customer Pipeline Service", version="1.0.0")


# GET /api/health
@app.get("/api/health")
def health_check():
    return {"status": "UP", "service": "pipeline-service"}


# POST /api/ingest
# Fetches all data from Flask and upserts into PostgreSQL
# Same as a @PostMapping service method that calls another microservice
@app.post("/api/ingest")
def ingest_customers(db: Session = Depends(get_db)):
    """
    Depends(get_db) = @Autowired in Spring Boot
    FastAPI injects the db session automatically into this function
    """
    try:
        # Step 1: Fetch all customers from Flask with auto-pagination
        customers = fetch_all_customers_from_flask()

        if not customers:
            raise HTTPException(status_code=404, detail="No customers found in Flask service")

        # Step 2: Upsert all into PostgreSQL
        records_processed = upsert_customers(db, customers)

        return {
            "status": "success",
            "records_processed": records_processed
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET /api/customers?page=1&limit=10
# Reads from PostgreSQL — NOT from Flask
@app.get("/api/customers")
def get_customers(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    """
    page and limit have default values — same as
    @RequestParam(defaultValue="1") in Spring Boot
    """
    # Calculate offset — same pagination math as Flask
    offset = (page - 1) * limit

    # Query PostgreSQL with pagination
    # Same as customerRepository.findAll(PageRequest.of(page, limit))
    customers = db.query(Customer).offset(offset).limit(limit).all()
    total = db.query(Customer).count()

    # Convert SQLAlchemy objects to dicts for JSON response
    # In Spring Boot this happens automatically via Jackson
    # In Python we need to do it manually
    result = []
    for c in customers:
        result.append({
            "customer_id":     c.customer_id,
            "first_name":      c.first_name,
            "last_name":       c.last_name,
            "email":           c.email,
            "phone":           c.phone,
            "address":         c.address,
            "date_of_birth":   str(c.date_of_birth) if c.date_of_birth else None,
            "account_balance": float(c.account_balance) if c.account_balance else None,
            "created_at":      str(c.created_at) if c.created_at else None
        })

    return {
        "data":  result,
        "total": total,
        "page":  page,
        "limit": limit
    }


# GET /api/customers/C001
@app.get("/api/customers/{customer_id}")
def get_customer_by_id(customer_id: str, db: Session = Depends(get_db)):
    """
    {customer_id} in path = @PathVariable in Spring Boot
    """
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        # HTTPException 404 = ResponseEntity.notFound() in Spring Boot
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    return {
        "data": {
            "customer_id":     customer.customer_id,
            "first_name":      customer.first_name,
            "last_name":       customer.last_name,
            "email":           customer.email,
            "phone":           customer.phone,
            "address":         customer.address,
            "date_of_birth":   str(customer.date_of_birth) if customer.date_of_birth else None,
            "account_balance": float(customer.account_balance) if customer.account_balance else None,
            "created_at":      str(customer.created_at) if customer.created_at else None
        }
    }