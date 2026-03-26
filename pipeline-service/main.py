from fastapi import FastAPI, HTTPException
from database import SessionLocal, engine
from models.customer import Customer
from services.ingestion import fetch_all_customers

app = FastAPI()
Customer.metadata.create_all(bind=engine)

@app.post("/api/ingest")
def ingest():
    db = SessionLocal()
    customers = fetch_all_customers()

    count = 0

    for c in customers:
        existing = db.query(Customer).filter_by(customer_id=c["customer_id"]).first()

        if existing:
            for key, value in c.items():
                setattr(existing, key, value)
        else:
            db.add(Customer(**c))

        count += 1

    db.commit()
    db.close()

    return {"status": "success", "records_processed": count}


@app.get("/api/customers")
def get_customers(page: int = 1, limit: int = 10):
    db = SessionLocal()
    offset = (page - 1) * limit

    data = db.query(Customer).offset(offset).limit(limit).all()
    return data


@app.get("/api/customers/{id}")
def get_customer(id: str):
    db = SessionLocal()
    customer = db.query(Customer).filter_by(customer_id=id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Not found")

    return customer

