from app.models.market_price import MarketPrice
from app.repository.base import BaseRepository
from sqlalchemy import select


class MarketPriceRepository(BaseRepository[MarketPrice]):
    model = MarketPrice

    async def get_by_product(self, product_id: int) -> list[MarketPrice]:
        return await self.get_all_by(product_id=product_id)

    async def get_latest_by_product(self, product_id: int) -> MarketPrice | None:
        statement = (
            select(MarketPrice)
            .where(MarketPrice.product_id == product_id)
            .order_by(MarketPrice.scraped_at.desc())
            .limit(1)
        )
        return await self.db.scalar(statement)
