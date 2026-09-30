import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

import ai_service, logic  # noqa: E402
from auth import create_token, current_user, hash_password, verify_password  # noqa: E402
from database import Base, engine, get_db  # noqa: E402
from models import FinancialRecord, User  # noqa: E402
from schemas import AdviceOut, LoginIn, RecordIn, RecordOut, RegisterIn, TokenOut  # noqa: E402

Base.metadata.create_all(engine)
app = FastAPI(title="Credit Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


def history(db: Session, user: User) -> list[FinancialRecord]:
    q = select(FinancialRecord).where(FinancialRecord.user_id == user.id).order_by(FinancialRecord.created_at, FinancialRecord.id)
    return list(db.scalars(q))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(name=body.name.strip(), email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    return TokenOut(access_token=create_token(user.id), name=user.name)


@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Wrong email or password")
    return TokenOut(access_token=create_token(user.id), name=user.name)


@app.post("/records", response_model=RecordOut, status_code=201)
def add_record(body: RecordIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Scenarios 1 and 4: save a snapshot; DTI and utilization are calculated here."""
    if body.credit_used > body.credit_limit > 0:
        raise HTTPException(422, "Credit used cannot be more than your credit limit")
    rec = FinancialRecord(
        user_id=user.id,
        **body.model_dump(),
        debt_to_income=logic.dti(body.monthly_income, body.monthly_debt_payments),
        utilization=logic.utilization(body.credit_limit, body.credit_used),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@app.get("/records", response_model=list[RecordOut])
def list_records(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return history(db, user)


@app.get("/dashboard")
def get_dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Scenario 3: history for the line chart, utilization for the pie, improvement delta."""
    return logic.dashboard(user.name, history(db, user))


@app.post("/advice", response_model=AdviceOut)
def advice(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Scenario 2: send the latest metrics to Gemini and return a 5-step plan."""
    records = history(db, user)
    if not records:
        raise HTTPException(400, "Add your financial details first")
    return ai_service.get_advice(records[-1])
