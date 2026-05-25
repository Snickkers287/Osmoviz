from __future__ import annotations
import csv
import io
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from backend.database import get_db, init_db
from backend.formulas import compute_stress_indices
from backend.models import Reading, Scenario
from backend.schemas import ( ComputeRequest, ReadingOut, ReadingBulkCreate, ScenarioCreate, ScenarioSummary, ScenarioOut, SimulateResponse, SimulateRequest, StressResultOut)
app = FastAPI(
    title="Osmoviz API", description="Plants physiological stress visualizer", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])


@app.on_event("startup")
def on_startup():
    init_db()
def _get_or_404(scenario_id: int, db: Session)-> Scenario:
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"scenario{scenario_id} not found")
    return s


def _scenario_out(s: Scenario, db: Session) -> ScenarioOut:
    count = db.query(Reading).filter(Reading.scenario_id == s.id).count()
    return ScenarioOut(
        id=s.id, name=s.name, description=s.description, crop_type=s.crop_type, location=s.location, elevation_m=s.elevation_m,
        latitude_deg=s.latitude_deg, created_at=s.created_at, reading_count=count,)

def _stress_out(sr) -> StressResultOut:
    return StressResultOut(
        vpd_kpa=sr.vpd_kpa, eto_mm_h=sr.eto_mm_h, heat_stress=sr.heat_stress, chilling_stress=sr.chilling_stress,
        vpd_high_stress=sr.vpd_high_stress, vpd_low_stress=sr.vpd_low_stress, light_high_stress=sr.light_high_stress,
        light_low_stress=sr.light_low_stress,waterlogging_stress=sr.waterlogging_stress,wilting_stress=sr.wilting_stress,
        overall_stress=sr.overall_stress,dominant_stress=sr.dominant_stress,stress_level=sr.stress_level,active_stresses=sr.active_stresses,
        recommendations=sr.recommendations,)

def  _reading_out(r: Reading, s:Scenario) -> ReadingOut:
    ts = r.timestamp
    sr = compute_stress_indices(
        T=r.temperature_c,RH=r.humidity_pct,lux=r.light_lux,soil_moisture_pct=r.soil_moisture_pct,wind_speed_ms=r.wind_speed_ms,
        elevation_m=s.elevation_m,latitude_deg=s.latitude_deg,day_of_year=ts.timetuple().tm_yday,hour=ts.hour,)

    return ReadingOut(
        id=r.id,scenario_id=r.scenario_id,timestamp=r.timestamp,  temperature_c=r.temperature_c, humidity_pct=r.humidity_pct,
        soil_moisture_pct=r.soil_moisture_pct, light_lux=r.light_lux, wind_speed_ms=r.wind_speed_ms,co2_ppm=r.co2_ppm,notes=r.notes,stress=_stress_out(sr),)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/scenarios",response_model=ScenarioOut,status_code=201)
def create_scenario(body:ScenarioCreate,db:Session=Depends(get_db)):
    s = Scenario(**body.model_dump())
    db.add(s); db.commit(); db.refresh(s)
    return _scenario_out(s, db)
