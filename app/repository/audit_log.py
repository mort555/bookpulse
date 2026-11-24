from app.models.audit_log import AuditLog
from app.repository.base import BaseRepository
from sqlalchemy import select


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def get_by_user(self, user_id: int) -> list[AuditLog]:
        return await self.get_all_by(user_id=user_id)

    async def get_by_entity(self, entity: str, entity_id: int) -> list[AuditLog]:
        statement = (
            select(AuditLog)
            .where(AuditLog.entity == entity, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        )
        result = await self.db.scalars(statement)
        return list(result.all())
