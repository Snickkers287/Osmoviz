from datetime import datetime
from sqlalchemy import Column, Float, DateTime, String, Integer, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    crop_type = Column(String(50), nullable=False, default="tomato")
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True, default="Suez, Egypt")
    elevation_m = Column(Float, nullable=False, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    latitude_deg = Column(Float, nullable=False, default=29.97)


    readings = relationship("Reading", back_populates="scenario", cascade="all, delete-orphan", order_by="Reading.timestamp")

class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), ondelete="CASCADE", nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, Index=True)
    temperature_c =Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    soil_moisture_pct = Column(Float, nullable=False)
    light_lux = Column(Float, nullable=False)
    wind_speed_ms = Column(Float, nullable=False, default=0.5)
    co2_ppm = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)
    scenario = relationship("Scenario", back_populates="readings")