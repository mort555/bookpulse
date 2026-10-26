from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.domain.entities import Money, PriceSnapshot


def test_money_uses_gbp_by_default() -> None:
    money = Money(amount=Decimal("12.50"))

    assert money.amount == Decimal("12.50")
    assert money.currency == "GBP"


def test_money_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(amount=Decimal("-1.00"))


def test_money_rejects_unsupported_currency() -> None:
    with pytest.raises(ValueError, match="Only GBP"):
        Money(amount=Decimal("10.00"), currency="USD")


def test_price_snapshot_stores_price_data() -> None:
    captured_at = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    price = Money(amount=Decimal("19.99"))

    snapshot = PriceSnapshot(
        supplier_id=1,
        product_name="Python Programming",
        price=price,
        captured_at=captured_at,
    )

    assert snapshot.supplier_id == 1
    assert snapshot.product_name == "Python Programming"
    assert snapshot.price == price
    assert snapshot.captured_at == captured_at


def test_money_is_immutable() -> None:
    money = Money(amount=Decimal("10.00"))

    with pytest.raises(AttributeError):
        money.amount = Decimal("20.00")  # type: ignore[misc]
