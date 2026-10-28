import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, JSON, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class AuditLog(Base):
    """Tracks administrative and analyst actions for accountability."""
    __tablename__ = "audit_logs"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    action = Column(String(50), nullable=False)
    entity_affected = Column(String(100), nullable=False)
    details = Column(JSON, nullable=False)
    timestamp = Column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog action={self.action} entity={self.entity_affected}>"
