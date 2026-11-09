import argparse
import logging
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.database.session import SessionFactory
from sqlalchemy import text
from sqlalchemy.orm import Session

# Додаємо корінь проєкту до шляху пошуку імпортів
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def seed_data(products_count: int, history_days: int, total_rows: int, seed: int):
    logger.info(
        "Starting seeding with parameters: products=%d, history_days=%d, rows=%d," \
        "seed=%d",
        products_count,
        history_days,
        total_rows,
        seed,
    )

    random.seed(seed)

    db: Session = SessionFactory()
    try:
        logger.info("Ensuring base categories and suppliers exist...")

        db.execute(
            text("""
            INSERT INTO categories (name, slug) 
            VALUES ('Fiction', 'fiction'), ('Sci-Fi', 'sci-fi'), ('Non-Fiction',
            'non-fiction')
            ON CONFLICT (name) DO NOTHING;
        """)
        )

        db.execute(
            text("""
            INSERT INTO suppliers (name, website_url, is_active) 
            VALUES ('Default Supplier', 'https://example.com', true)
            ON CONFLICT (name) DO NOTHING;
        """)
        )
        db.commit()

        category_ids = [
            row[0] for row in db.execute(text("SELECT id FROM categories;")).fetchall()
        ]
        if not category_ids:
            raise ValueError("No categories found in database.")

        logger.info("Generating products...")
        existing_products = db.execute(text("SELECT id FROM products;")).fetchall()

        if len(existing_products) < products_count:
            products_to_create = products_count - len(existing_products)
            batch_products: list[dict[str, Any]] = []
            for i in range(products_to_create):
                idx = len(existing_products) + i + 1
                batch_products.append(
                    {
                        "upc": f"UPC-{seed}-{idx:06d}",
                        "title": f"Book Title {idx} ({random.choice(['Alpha', 'Beta',
                        'Gamma', 'Delta'])})",
                        "category_id": random.choice(category_ids),
                        "description": f"Auto-generated description for book {idx}",
                        "rating": random.randint(1, 5),
                        "image_url": "https://example.com/image.jpg",
                        "source_url": "https://example.com/source",
                    }
                )

            db.execute(
                text("""
                    INSERT INTO products (upc, title, category_id, description, rating,
                    image_url, source_url)
                    VALUES (:upc, :title, :category_id, :description, :rating,
                    :image_url, :source_url)
                    ON CONFLICT (upc) DO NOTHING;
                """),
                batch_products,
            )
            db.commit()

        product_ids = [
            row[0] for row in db.execute(text("SELECT id FROM products;")).fetchall()
        ]
        logger.info("Total available products in DB: %d", len(product_ids))

        logger.info("Generating market price history...")
        now = datetime.now(UTC)
        start_date = now - timedelta(days=history_days)

        batch_size = 50000
        inserted_rows = 0

        while inserted_rows < total_rows:
            current_batch_size = min(batch_size, total_rows - inserted_rows)
            price_batch: list[dict[str, Any]] = []

            for _ in range(current_batch_size):
                prod_id = random.choice(product_ids)
                random_seconds = random.randint(0, history_days * 24 * 3600)
                scraped_at = start_date + timedelta(seconds=random_seconds)

                price_excl = round(random.uniform(10.0, 500.0), 2)
                tax = round(price_excl * 0.2, 2)
                price_incl = round(price_excl + tax, 2)
                in_stock = random.randint(0, 50)

                price_batch.append(
                    {
                        "product_id": prod_id,
                        "price_incl_tax": price_incl,
                        "price_excl_tax": price_excl,
                        "tax": tax,
                        "in_stock": in_stock,
                        "scraped_at": scraped_at,
                    }
                )

            db.execute(
                text("""
                    INSERT INTO market_prices (product_id, price_incl_tax,
                    price_excl_tax,tax, in_stock, scraped_at)
                    VALUES (:product_id, :price_incl_tax, :price_excl_tax, :tax,
                    :in_stock,:scraped_at)
                """),
                price_batch,
            )
            db.commit()
            inserted_rows += current_batch_size
            logger.info("Inserted %d/%d rows...", inserted_rows, total_rows)

        logger.info("Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        logger.error("Error during seeding: %s", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed demo data for bookpulse performance tests."
    )
    parser.add_argument(
        "--products", type=int, default=1000, help="Number of products to generate"
    )
    parser.add_argument(
        "--history-days",
        type=int,
        default=90,
        help="Number of history days for prices",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=1000000,
        help="Total rows of market prices to generate",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    seed_data(
        products_count=args.products,
        history_days=args.history_days,
        total_rows=args.rows,
        seed=args.seed,
    )
