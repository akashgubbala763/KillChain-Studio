import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, DateTime,
)
from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class BehaviorBaseline(Base):
    """Rolling statistical baseline per monitored entity (IP, Host, User)."""
    __tablename__ = "behavior_baselines"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    entity_type = Column(String(20), nullable=False)  # IP, HOST, USER
    entity_id = Column(String(100), nullable=False, index=True)

    # Mean metrics
    avg_connections_per_hour = Column(Float, nullable=False, default=0.0)
    avg_bytes_out_per_hour = Column(Float, nullable=False, default=0.0)
    avg_unique_dest_ports = Column(Float, nullable=False, default=0.0)
    avg_failed_logins_per_hour = Column(Float, nullable=False, default=0.0)

    # Standard deviation metrics
    std_dev_connections = Column(Float, nullable=False, default=1.0)
    std_dev_bytes_out = Column(Float, nullable=False, default=1.0)
    std_dev_ports = Column(Float, nullable=False, default=1.0)
    std_dev_failed_logins = Column(Float, nullable=False, default=1.0)

    # Metadata
    baseline_start = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    baseline_updated = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    sample_count = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<BehaviorBaseline {self.entity_type}:{self.entity_id} samples={self.sample_count}>"
