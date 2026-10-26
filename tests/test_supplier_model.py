from app.infra.database.models import Supplier


def test_supplier_model_table_and_columns() -> None:
    assert Supplier.__tablename__ == "suppliers"

    assert "id" in Supplier.__table__.columns
    assert "name" in Supplier.__table__.columns
    assert "website_url" in Supplier.__table__.columns
    assert "is_active" in Supplier.__table__.columns


def test_supplier_name_is_unique() -> None:
    name_column = Supplier.__table__.columns["name"]

    assert name_column.unique is True
    assert name_column.nullable is False


def test_supplier_website_is_required() -> None:
    website_column = Supplier.__table__.columns["website_url"]

    assert website_column.nullable is False
