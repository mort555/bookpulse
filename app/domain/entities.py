from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "GBP"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative.")

        if self.currency != "GBP":
            raise ValueError("Only GBP currency is supported.")


@dataclass(frozen=True, slots=True)
class PriceSnapshot:
    supplier_id: int
    product_name: str
    price: Money
    captured_at: datetime
