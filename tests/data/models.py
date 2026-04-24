from pydantic import BaseModel, Field, field_validator
from typing import Literal

class TickerMessage(BaseModel):
    ticker: str
    price: float = Field(gt=0)
    status: Literal["LIVE", "CLOSED"]

    # mode='after' чтобы проверка шла после базовой обработки строки
    @field_validator('ticker', mode='after')
    @classmethod
    def ticker_must_be_uppercase(cls, v: str) -> str:
        if v != v.upper():
            raise ValueError('ticker must be uppercase')
        return v
