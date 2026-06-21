from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Farm assessment ----------

class FarmInput(BaseModel):
    crop_type: str
    farm_size_acres: float
    irrigation_level: str       # "low" / "medium" / "high"
    soil_moisture: str          # "dry" / "moderate" / "wet"
    water_usage_litres: float = 0


class FarmAssessmentResponse(BaseModel):
    health_status: str
    carbon_estimate: float
    recommendations: str
    timestamp: datetime


class FarmHistoryItem(BaseModel):
    crop_type: str
    farm_size_acres: float
    irrigation_level: str
    soil_moisture: str
    health_status: str
    carbon_estimate: float
    recommendations: str
    timestamp: datetime

    class Config:
        from_attributes = True