import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, JSON, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Incident(Base):
    """Aggregated security incident composed of correlated events."""
    __tablename__ = "incidents"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    incident_code = Column(
        String(30), unique=True, nullable=False, index=True
    )
    title = Column(String(200), nullable=False)
    primary_entity = Column(String(100), nullable=False, index=True)
    attack_category = Column(String(50), nullable=False)
    status = Column(
        String(20), nullable=False, default="OPEN"
    )  # OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    severity = Column(String(15), nullable=False, default="LOW")
    current_risk_score = Column(Float, nullable=False, default=0.0)
    confidence_rating = Column(Float, nullable=False, default=0.0)
    signal_consensus = Column(
        String(25), nullable=False, default="CONFLICTING"
    )  # STRONG_AGREEMENT, MODERATE, CONFLICTING
    start_time = Column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )
    assigned_user_id = Column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    assigned_user = relationship("User", back_populates="assigned_incidents")
    incident_events = relationship(
        "IncidentEvent", back_populates="incident", lazy="selectin",
        cascade="all, delete-orphan",
        order_by="IncidentEvent.sequence_order",
    )
    risk_scores = relationship(
        "RiskScore", back_populates="incident", lazy="selectin",
        cascade="all, delete-orphan",
        order_by="RiskScore.calculated_at",
    )

    def __repr__(self):
        return f"<Incident {self.incident_code} severity={self.severity} risk={self.current_risk_score}>"


class IncidentEvent(Base):
    """Cross-reference linking events to an incident with kill-chain metadata."""
    __tablename__ = "incident_events"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    incident_id = Column(
        String(36), ForeignKey("incidents.id"), nullable=False, index=True
    )
    event_id = Column(
        String(36), ForeignKey("network_events.id"), nullable=False, index=True
    )
    sequence_order = Column(Integer, nullable=False, index=True)
    kill_chain_phase = Column(String(40), nullable=False)
    running_risk_score = Column(Float, nullable=False, default=0.0)
    event_timestamp = Column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Relationships
    incident = relationship("Incident", back_populates="incident_events")
    event = relationship("NetworkEvent", back_populates="incident_events")

    def __repr__(self):
        return (
            f"<IncidentEvent incident={self.incident_id} "
            f"step={self.sequence_order} phase={self.kill_chain_phase}>"
        )


class RiskScore(Base):
    """Forensic history of explainable risk score calculations."""
    __tablename__ = "risk_scores"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    incident_id = Column(
        String(36), ForeignKey("incidents.id"), nullable=False, index=True
    )
    calculated_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    total_score = Column(Float, nullable=False)
    rule_component = Column(Float, nullable=False, default=0.0)
    ml_component = Column(Float, nullable=False, default=0.0)
    anomaly_component = Column(Float, nullable=False, default=0.0)
    deviation_component = Column(Float, nullable=False, default=0.0)
    correlation_component = Column(Float, nullable=False, default=0.0)
    explanation = Column(JSON, nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="risk_scores")

    def __repr__(self):
        return f"<RiskScore incident={self.incident_id} total={self.total_score}>"
