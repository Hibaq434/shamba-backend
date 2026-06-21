from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessments = relationship(
        "Assessment", back_populates="farmer", cascade="all, delete-orphan"
    )


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    crop_type = Column(String, nullable=False)
    farm_size_acres = Column(Float, nullable=False)
    irrigation_level = Column(String, nullable=False)
    soil_moisture = Column(String, nullable=False)
    water_usage_litres = Column(Float, default=0)

    health_status = Column(String, nullable=False)
    carbon_estimate = Column(Float, nullable=False)
    recommendations = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("User", back_populates="assessments")