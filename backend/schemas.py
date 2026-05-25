from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator



class ScenarioCreate(BaseModel):
    name:str           = Field(..., min_length=1, max_length=200)
    description:Optional[str] = None
    crop_type:str           = "tomato"
    location:  Optional[str] = "Ismailia, Egypt"
    elevation_m:float         = Field(10.0,  ge=0,   le=5000)
    latitude_deg: float         = Field(30.60, ge=-90, le=90)

class ScenarioOut(BaseModel):
    id:  int
    name: str
    description:Optional[str]
    crop_type:   str
    location:Optional[str]
    elevation_m:float
    latitude_deg:float
    created_at:datetime
    reading_count:int = 0
    model_config = {"from_attributes": True}
class ReadingCreate(BaseModel):
    timestamp:datetime
    temperature_c: float = Field(..., ge=-10,  le=70)
    humidity_pct: float = Field(..., ge=0,    le=100)
    soil_moisture_pct: float = Field(..., ge=0,    le=100)
    light_lux:  float = Field(..., ge=0,    le=150000)
    wind_speed_ms:float = Field(0.5, ge=0,    le=30)
    co2_ppm:Optional[float] = Field(None, ge=0, le=5000)
    notes:Optional[str]   = Field(None, max_length=500)
class ReadingBulkCreate(BaseModel):
    readings: List[ReadingCreate]



class StressResultOut(BaseModel):
    vpd_kpa:float
    eto_mm_h:float
    etc_mm_h:float
    heat_stress:float
    chilling_stress:float
    vpd_high_stress:float
    vpd_low_stress:float
    light_high_stress:float
    light_low_stress:float
    waterlogging_stress: float
    wilting_stress:float
    overall_stress:       float
    dominant_stress:str
    active_stresses:list[str]
    stress_level:    str
    recommendations:list[str]
class ReadingOut(BaseModel):
    id:int
    scenario_id:int
    timestamp:datetime
    temperature_c:float
    humidity_pct:float
    soil_moisture_pct: float
    light_lux:float
    wind_speed_ms:float
    co2_ppm:Optional[float]
    stress:StressResultOut
    notes:Optional[str]
    model_config = {"from_attributes": True}


class ComputeRequest(BaseModel):
    temperature_c:float = Field(..., ge=-10, le=70)
    humidity_pct:float = Field(..., ge=0,   le=100)
    soil_moisture_pct: float = Field(..., ge=0,   le=100)
    light_lux:float = Field(..., ge=0,   le=150000)
    wind_speed_ms:float = Field(0.5, ge=0,   le=30)
    elevation_m:float = Field(10.0,  ge=0, le=5000)
    latitude_deg:   float = Field(30.60, ge=-90, le=90)
    crop_type:str   = "tomato"

class StressEventSchema(BaseModel):
    type:str = Field(..., description="heat_wave | drought | overwatering | low_light | ideal")
    start_hour:int = Field(..., ge=0)
    end_hour:int
    @model_validator(mode="after")
    def check_hours(self) -> "StressEventSchema":
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self
class SimulateRequest(BaseModel):
    scenario_id:int

    duration_hours:int   = Field(72,      ge=1,  le=720)
    interval_minutes:int   = Field(60,      ge=15, le=360)
    base_temp_c:  float = Field(28.0,    ge=5,  le=50)
    base_humidity_pct:float = Field(65.0,    ge=10, le=100)
    base_soil_moisture_pct: float = Field(70.0,    ge=0,  le=100)
    base_light_lux:float = Field(35000.0, ge=0,  le=150000)
    wind_speed_ms:float = Field(0.5,     ge=0)
    start_datetime:Optional[datetime] = None
    stress_event:Optional[StressEventSchema] = None


class SimulateResponse(BaseModel):
    scenario_id:int
    readings_created: int
    message:str


class ScenarioSummary(BaseModel):
    scenario:ScenarioOut
    total_readings:int
    avg_overall_stress: float
    max_overall_stress: float
    time_in_stress:dict
    dominant_stresses:  dict
    avg_vpd:float
    avg_eto:   float
    avg_temp:
    avg_humidity:float
    avg_soil_moisture:float
    max_soil_moisture:   float
    min_soil_moisture:    float