from __future__ import annotations
import csv
import io
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, session
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
    from backend.seed_data import seed
    seed()


def _get_or_404(scenario_id: int, db: Session) -> Scenario:
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found.")
    return s

def _scenario_out(s: Scenario, db: Session) -> ScenarioOut:
    count = db.query(Reading).filter(Reading.scenario_id == s.id).count()
    return ScenarioOut(
        id=s.id, name=s.name, description=s.description, crop_type=s.crop_type, location=s.location, elevation_m=s.elevation_m,
        latitude_deg=s.latitude_deg, created_at=s.created_at, reading_count=count,)

def _stress_out(sr) -> StressResultOut:
    return StressResultOut(
        vpd_kpa=sr.vpd_kpa, eto_mm_h=sr.eto_mm_h, etc_mm_h=sr.etc_mm_h,
        heat_stress=sr.heat_stress, chilling_stress=sr.chilling_stress,
        vpd_high_stress=sr.vpd_high_stress, vpd_low_stress=sr.vpd_low_stress,
        light_high_stress=sr.light_high_stress, light_low_stress=sr.light_low_stress,
        waterlogging_stress=sr.waterlogging_stress, wilting_stress=sr.wilting_stress,
        overall_stress=sr.overall_stress, dominant_stress=sr.dominant_stress,
        stress_level=sr.stress_level, active_stresses=sr.active_stresses,
        recommendations=sr.recommendations,)

def _reading_out(r: Reading, s: Scenario) -> ReadingOut:
    ts = r.timestamp
    sr = compute_stress_indices(
        T=r.temperature_c, RH=r.humidity_pct, lux=r.light_lux,
        soil_moisture_pct=r.soil_moisture_pct, wind_speed_ms=r.wind_speed_ms,
        elevation_m=s.elevation_m, latitude_deg=s.latitude_deg,
        day_of_year=ts.timetuple().tm_yday, hour=ts.hour,)

    return ReadingOut(
        id=r.id, scenario_id=r.scenario_id, timestamp=r.timestamp,
        temperature_c=r.temperature_c, humidity_pct=r.humidity_pct,
        soil_moisture_pct=r.soil_moisture_pct, light_lux=r.light_lux,
        wind_speed_ms=r.wind_speed_ms, co2_ppm=r.co2_ppm, notes=r.notes,
        stress=_stress_out(sr),)



@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/scenarios", response_model=ScenarioOut, status_code=201)
def create_scenario(body: ScenarioCreate, db: Session=Depends(get_db)):
    s = Scenario(**body.model_dump())
    db.add(s); db.commit(); db.refresh(s)
    return _scenario_out(s, db)

@app.get("/api/scenarios", response_model=List[ScenarioOut])
def list_scenarios(db: Session=Depends(get_db)):
    return [_scenario_out(s, db) for s in db.query(Scenario).order_by(Scenario.created_at.desc()).all()]

@app.get("/api/scenarios/{scenario_id}", response_model=ScenarioOut)
def get_scenario(scenario_id: int, db: Session=Depends(get_db)):
    return _scenario_out(_get_or_404(scenario_id, db), db)

@app.delete("/api/scenarios/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: int, db: Session=Depends(get_db)):
    db.delete(_get_or_404(scenario_id, db)); db.commit()

@app.post("/api/scenarios/{scenario_id}/readings", status_code=201)
def add_readings(scenario_id: int, body: ReadingBulkCreate, db: Session=Depends(get_db)):
    _get_or_404(scenario_id, db)
    db.bulk_save_objects([Reading(scenario_id=scenario_id, **r.model_dump()) for r in body.readings])
    db.commit()
    return {"inserted": len(body.readings)}

@app.get("/api/scenarios/{scenario_id}/readings", response_model=list[ReadingOut])
def get_readings(
        scenario_id: int, limit: Optional[int] = Query(None, ge=1, le=5000),
        offset: int = Query(0, ge=0),
        db: Session=Depends(get_db),
):
    s = _get_or_404(scenario_id, db)
    q = db.query(Reading).filter(Reading.scenario_id == scenario_id).order_by(Reading.timestamp)
    if offset: q = q.offset(offset)
    if limit: q = q.limit(limit)
    return [_reading_out(r, s) for r in q.all()]

@app.get("/api/scenarios/{scenario_id}/readings/export")
def export_csv(scenario_id: int, db: Session=Depends(get_db)):
    s = _get_or_404(scenario_id, db)
    readings = db.query(Reading).filter(Reading.scenario_id == s.id).order_by(Reading.timestamp).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["timestamp","temperature_c","humidity_pct","soil_moisture_pct","light_lux",
                "vpd_kpa","eto_mm_h","overall_stress","stress_level","dominant_stress"])
    for r in readings:
        ro = _reading_out(r, s)
        w.writerow([ro.timestamp.isoformat(), ro.temperature_c, ro.humidity_pct,
                    ro.soil_moisture_pct, ro.light_lux, ro.stress.vpd_kpa,
                    ro.stress.eto_mm_h, ro.stress.overall_stress,
                    ro.stress.stress_level, ro.stress.dominant_stress])
    buf.seek(0)
    fname = f"osmoviz_{scenario_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={fname}"})

@app.get("/api/scenarios/{scenario_id}/summary", response_model=ScenarioSummary)
def get_summary(scenario_id: int, db: Session=Depends(get_db)):
    s = _get_or_404(scenario_id, db)
    readings = db.query(Reading).filter(Reading.scenario_id == s.id).order_by(Reading.timestamp).all()

    if not readings:
        return ScenarioSummary(
            scenario=_scenario_out(s, db), total_readings=0, avg_overall_stress=0,
            max_overall_stress=0, time_in_stress={"optimal":100,"mild":0.0,"moderate":0.0,"severe":0.0},
            dominant_stresses={}, avg_vpd=0.0, avg_eto=0.0, avg_temp=0.0, avg_humidity=0.0,
            avg_soil_moisture=0.0, max_soil_moisture=0.0, min_soil_moisture=0.0,)

    stress_list = [_reading_out(r, s).stress for r in readings]
    n = len(stress_list)
    levels: dict[str,int] = {"optimal": 0, "mild": 0, "moderate": 0, "severe": 0}
    dom: dict[str,int] = {}



    for sr in stress_list:
        levels[sr.stress_level] = levels.get(sr.stress_level, 0) + 1
        dom[sr.dominant_stress] = dom.get(sr.dominant_stress, 0) + 1

    soil_vals = [r.soil_moisture_pct for r in readings]

    return ScenarioSummary(
        scenario=_scenario_out(s, db),
        total_readings=n,
        avg_overall_stress=round(sum(r.overall_stress for r in stress_list) / n, 2),
        max_overall_stress=round(max(r.overall_stress for r in stress_list), 2),
        time_in_stress={k: round(v / n * 100, 1) for k, v in levels.items()},
        dominant_stresses=dom,
        avg_vpd=round(sum(r.vpd_kpa for r in stress_list) / n, 4),
        avg_eto=round(sum(r.eto_mm_h for r in stress_list) / n, 4),
        avg_temp=round(sum(r.temperature_c for r in readings) / n, 2),
        avg_humidity=round(sum(r.humidity_pct for r in readings) / n, 2),
        avg_soil_moisture=round(sum(soil_vals) / n, 2),
        max_soil_moisture=round(max(soil_vals), 2),
        min_soil_moisture=round(min(soil_vals), 2),)


@app.post("/api/compute", response_model=StressResultOut)
def compute_adhoc(body: ComputeRequest):
    now = datetime.utcnow()
    sr = compute_stress_indices(
        T=body.temperature_c, RH=body.humidity_pct, lux=body.light_lux,
        wind_speed_ms=body.wind_speed_ms, soil_moisture_pct=body.soil_moisture_pct,
        elevation_m=body.elevation_m, latitude_deg=body.latitude_deg,
        day_of_year=now.timetuple().tm_yday, hour=now.hour,)
    return _stress_out(sr)


@app.post("/api/simulate", response_model=SimulateResponse, status_code=201)
def simulate(body: SimulateRequest, db: Session=Depends(get_db)):
    _get_or_404(body.scenario_id, db)
    start = body.start_datetime or datetime(2026, 4, 14, 6, 0, 0)
    n_steps = int(body.duration_hours * 3600 / (body.interval_minutes * 60))
    readings = []

    for i in range(n_steps):
        elapsed_h = i * body.interval_minutes / 60
        ts = start + timedelta(hours=elapsed_h)
        h = ts.hour + ts.minute / 60.0
        T = body.base_temp_c + 5.0 * math.cos((h - 14) / 24 * 2 * math.pi + math.pi)
        RH = max(30., min(100.0, body.base_humidity_pct - 2.0 * (T - body.base_temp_c)))
        lux = body.base_light_lux * math.sin(math.pi * (h - 6) / 14) if 6 <= h <= 20.0 else 15
        sm = max(30.0, body.base_soil_moisture_pct - 0.3 * elapsed_h)

        if body.stress_event:
            ev = body.stress_event
            if ev.start_hour <= elapsed_h < ev.end_hour:
                if ev.type == "heat_wave": T += 8.0; RH -= 10
                elif ev.type == "drought": sm = max(18.0, sm - 30)
                elif ev.type == "overwatering": sm = min(100.0, sm + 30.0)
                elif ev.type == "low_light": lux *= 0.20
                RH = max(10.0, min(100.0, RH))

        T += random.uniform(-0.3, 0.3)
        RH += random.uniform(-0.5, 0.5)
        sm += random.uniform(-0.2, 0.2)
        lux = max(0, lux + random.uniform(-200.0, 200))

        readings.append(Reading(
            scenario_id=body.scenario_id, timestamp=ts,
            temperature_c=round(T, 2),
            humidity_pct=round(max(10, min(100, RH)), 1),
            soil_moisture_pct=round(max(0.0, min(100.0, sm)), 1),
            light_lux=round(max(0.0, lux), 0),
            wind_speed_ms=body.wind_speed_ms,
        ))

    db.bulk_save_objects(readings); db.commit()
    return SimulateResponse(
        scenario_id=body.scenario_id, readings_created=len(readings),
        message=f"Generated {len(readings)} readings over {body.duration_hours}h.",)
_FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")