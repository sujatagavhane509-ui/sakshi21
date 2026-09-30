from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str


class RecordIn(BaseModel):
    credit_score: int = Field(ge=300, le=900)
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(ge=0)
    monthly_debt_payments: float = Field(ge=0)
    credit_limit: float = Field(ge=0)
    credit_used: float = Field(ge=0)
    missed_payments: int = Field(ge=0, default=0)


class RecordOut(RecordIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    debt_to_income: float
    utilization: float
    created_at: datetime


class AdviceOut(BaseModel):
    summary: str
    steps: list[str]
    source: str  # "gemini" or "fallback"
