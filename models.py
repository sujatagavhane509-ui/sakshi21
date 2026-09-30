from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    records: Mapped[list["FinancialRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class FinancialRecord(Base):
    """One snapshot of a user's finances. The history of snapshots drives the charts."""
    __tablename__ = "financial_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    credit_score: Mapped[int] = mapped_column(Integer)
    monthly_income: Mapped[float] = mapped_column(Float)
    monthly_expenses: Mapped[float] = mapped_column(Float)
    monthly_debt_payments: Mapped[float] = mapped_column(Float)  # total EMIs
    credit_limit: Mapped[float] = mapped_column(Float)
    credit_used: Mapped[float] = mapped_column(Float)
    missed_payments: Mapped[int] = mapped_column(Integer, default=0)
    debt_to_income: Mapped[float] = mapped_column(Float)  # percent, computed on save
    utilization: Mapped[float] = mapped_column(Float)  # percent, computed on save
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    user: Mapped[User] = relationship(back_populates="records")
