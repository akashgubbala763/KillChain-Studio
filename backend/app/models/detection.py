import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Float, DateTime, Text, JSON, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class DetectionRule(Base):
    """Configurable deterministic detection rules."""
    __tablename__ = "detection_rules"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rule_code = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(15), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    category = Column(String(30), nullable=False)   # RECON, ACCESS, LATERAL, EXFIL
    parameters = Column(JSON, nullable=False)        # threshold, window_sec, etc.
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    # Relationships
    matches = relationship(
        "RuleMatch", back_populates="rule", lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<DetectionRule {self.rule_code}: {self.name} severity={self.severity}>"


class RuleMatch(Base):
    """Links a specific event to the rule it violated, with forensic evidence."""
    __tablename__ = "rule_matches"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rule_id = Column(
        String(36), ForeignKey("detection_rules.id"), nullable=False, index=True
    )
    event_id = Column(
        String(36), ForeignKey("network_events.id"), nullable=False, index=True
    )
    matched_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    severity = Column(String(15), nullable=False)
    evidence_details = Column(JSON, nullable=False)

    # Relationships
    rule = relationship("DetectionRule", back_populates="matches")
    event = relationship("NetworkEvent", back_populates="rule_matches")

    def __repr__(self):
        return f"<RuleMatch rule={self.rule_id} event={self.event_id}>"


class MLPrediction(Base):
    """Supervised Random Forest classification output for an event."""
    __tablename__ = "ml_predictions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    event_id = Column(
        String(36), ForeignKey("network_events.id"), nullable=False, index=True
    )
    predicted_class = Column(String(30), nullable=False)
    confidence_score = Column(Float, nullable=False)
    class_probabilities = Column(JSON, nullable=False)
    model_version = Column(String(20), nullable=False, default="v1.0")
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # Relationships
    event = relationship("NetworkEvent", back_populates="ml_predictions")

    def __repr__(self):
        return f"<MLPrediction class={self.predicted_class} conf={self.confidence_score:.2f}>"


class AnomalyResult(Base):
    """Isolation Forest unsupervised anomaly detection output for an event."""
    __tablename__ = "anomaly_results"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    event_id = Column(
        String(36), ForeignKey("network_events.id"), nullable=False, index=True
    )
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, nullable=False, index=True)
    feature_contributions = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # Relationships
    event = relationship("NetworkEvent", back_populates="anomaly_results")

    def __repr__(self):
        return f"<AnomalyResult score={self.anomaly_score:.3f} anomaly={self.is_anomaly}>"
