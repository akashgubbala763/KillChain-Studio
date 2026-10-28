import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, BigInteger, DateTime, JSON,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class NetworkEvent(Base):
    __tablename__ = "network_events"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    timestamp = Column(
        DateTime(timezone=True), nullable=False, index=True
    )
    source_ip = Column(String(45), nullable=False, index=True)
    destination_ip = Column(String(45), nullable=False, index=True)
    source_port = Column(Integer, nullable=False)
    destination_port = Column(Integer, nullable=False, index=True)
    protocol = Column(String(10), nullable=False, index=True)
    event_type = Column(String(30), nullable=False, index=True)
    bytes_sent = Column(BigInteger, nullable=False, default=0)
    bytes_received = Column(BigInteger, nullable=False, default=0)
    packets = Column(Integer, default=1)
    tcp_flags = Column(String(30), nullable=True)
    user_identifier = Column(String(100), nullable=True, index=True)
    device_hostname = Column(String(100), nullable=True, index=True)
    raw_payload = Column(JSON, nullable=True)
    ingested_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )

    # Relationships
    rule_matches = relationship(
        "RuleMatch", back_populates="event", lazy="selectin",
        cascade="all, delete-orphan",
    )
    ml_predictions = relationship(
        "MLPrediction", back_populates="event", lazy="selectin",
        cascade="all, delete-orphan",
    )
    anomaly_results = relationship(
        "AnomalyResult", back_populates="event", lazy="selectin",
        cascade="all, delete-orphan",
    )
    incident_events = relationship(
        "IncidentEvent", back_populates="event", lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<NetworkEvent {self.source_ip}:{self.source_port} -> "
            f"{self.destination_ip}:{self.destination_port} "
            f"proto={self.protocol} type={self.event_type}>"
        )
