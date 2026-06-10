from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("EmailScan", back_populates="user")


class EmailScan(Base):
    __tablename__ = "email_scans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    email_subject = Column(String(255))
    email_content = Column(Text, nullable=False)

    prediction = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)

    processing_time_ms = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    reasons = relationship(
        "ScanReason",
        back_populates="scan",
        cascade="all, delete-orphan"
    )


class ScanReason(Base):
    __tablename__ = "scan_reasons"

    id = Column(Integer, primary_key=True, index=True)

    scan_id = Column(Integer, ForeignKey("email_scans.id"))

    reason = Column(String(255), nullable=False)

    severity = Column(String(50))

    scan = relationship("EmailScan", back_populates="reasons")


class SuspiciousURL(Base):
    __tablename__ = "suspicious_urls"

    id = Column(Integer, primary_key=True, index=True)

    url = Column(Text, nullable=False)

    domain = Column(String(255))

    risk_level = Column(String(50))

    times_detected = Column(Integer, default=1)

    first_seen = Column(DateTime, default=datetime.utcnow)

    last_seen = Column(DateTime, default=datetime.utcnow)


class PhishingIndicator(Base):
    __tablename__ = "phishing_indicators"

    id = Column(Integer, primary_key=True, index=True)

    indicator = Column(String(255), nullable=False)

    category = Column(String(100))

    risk_points = Column(Integer, default=0)


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)

    model_version = Column(String(50))

    accuracy = Column(Float)

    precision = Column(Float)

    recall = Column(Float)

    f1_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
