import requests
from datetime import datetime, date
from sqlalchemy.orm import Session
from models.customer import Customer

# Flask mock server URL — uses Docker service name "mock-server"
# Same as calling another microservice via RestTemplate in Spring Boot
FLASK_BASE_URL = "http://mock-server:5000"


def fetch_all_customers_from_flask():
    """
    Fetches ALL pages from Flask API with auto-pagination.
    Same as calling a paginated REST API with WebClient in Spring Boot
    and collecting all pages into one list.
    """
    all_customers = []
    page = 1
    limit = 10  # fetch 10 per page

    while True:
        # requests.get() = RestTemplate.getForObject() in Spring Boot
        response = requests.get(
            f"{FLASK_BASE_URL}/api/customers",
            params={"page": page, "limit": limit}
        )

        # Raise exception if HTTP status is 4xx or 5xx
        response.raise_for_status()

        data = response.json()
        customers = data.get("data", [])

        # If no customers returned, we've gone past the last page
        if not customers:
            break

        all_customers.extend(customers)

        # If we fetched less than limit, this was the last page
        if len(customers) < limit:
            break

        page += 1

    return all_customers


def parse_date(value):
    """Parse date string to Python date object. Returns None if empty."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_datetime(value):
    """Parse datetime string to Python datetime object. Returns None if empty."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def upsert_customers(db: Session, customers: list):
    """
    Upsert logic — INSERT if not exists, UPDATE if exists.
    Same as JPA saveOrUpdate() or CrudRepository.save() in Spring Boot.

    db     = EntityManager / JPA Session
    customers = list of customer dicts from Flask JSON
    """
    records_processed = 0

    for c in customers:
        # Check if customer already exists in DB
        # Same as customerRepository.findById(id) in Spring Boot
        existing = db.query(Customer).filter(
            Customer.customer_id == c['customer_id']
        ).first()

        if existing:
            # UPDATE — customer already exists, update all fields
            existing.first_name      = c.get('first_name')
            existing.last_name       = c.get('last_name')
            existing.email           = c.get('email')
            existing.phone           = c.get('phone')
            existing.address         = c.get('address')
            existing.date_of_birth   = parse_date(c.get('date_of_birth'))
            existing.account_balance = c.get('account_balance')
            existing.created_at      = parse_datetime(c.get('created_at'))
        else:
            # INSERT — new customer, create new record
            # Same as new Customer() then customerRepository.save(customer)
            new_customer = Customer(
                customer_id     = c.get('customer_id'),
                first_name      = c.get('first_name'),
                last_name       = c.get('last_name'),
                email           = c.get('email'),
                phone           = c.get('phone'),
                address         = c.get('address'),
                date_of_birth   = parse_date(c.get('date_of_birth')),
                account_balance = c.get('account_balance'),
                created_at      = parse_datetime(c.get('created_at'))
            )
            db.add(new_customer)

        records_processed += 1

    # Commit all changes — same as entityManager.flush() in Spring Boot
    db.commit()

    return records_processed