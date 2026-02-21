from pydantic import BaseModel
from typing import List, Optional

class Transaction(BaseModel):
    date: str
    amount: float
    ceiling: float
    remanent: float

class TransactionOutput(BaseModel):
    date: str
    amount: float
    ceiling: float
    remanent: float
    inKPeriod: Optional[bool] = None
    message: Optional[str] = None

    class Config:
        json_encoders = {
            float: lambda v: float(f"{v:.2f}")
        }

class ValidatorRequest(BaseModel):
    wage: float
    transactions: List[Transaction]

class ValidatorResponse(BaseModel):
    valid: List[TransactionOutput]
    invalid: List[TransactionOutput]

class FilterTransaction(BaseModel):
    date: str
    amount: float
    ceiling: float
    remanent: float
    inKPeriod: Optional[bool] = None
    message: Optional[str] = None

class FilterResponse(BaseModel):
    valid: List[FilterTransaction]
    invalid: List[FilterTransaction]
    