from __future__ import annotations
from datetime import datetime
from backend.database import SessionLocal, init_db
from backend.models import Reading, Scenario


def __parse_ts(s: str) -> datetime:
    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse {s!r}")

RAW_DATA =[
    ("04/14/2026 6:28:00", 22, 83, 11561, 35, "Startup Morning"),
    ("04/14/2026 6:28:30", 21.9, 82, 12354, 39, "Morning"),
    ("04/14/2026 6:29:00", 21.7, 82.5, 13275, 49, "Morning"),
    ("04/14/2026 6:29:30", 21.5, 81, 12591,56, "Morning, Start of Irrigation Cycle"),
    ("04/14/2026 6:30:00", 21.6, 80, 12874, 78,"Morning"),
    ("04/14/2026 6:30:30", 21.4, 79.2, 11956, 77,"Morning"),
    ("04/14/2026 6:31:00", 21.3, 78, 13545, 78,"Morning"),
    ("04/14/2026 6:31:30", 21.2, 77.9, 12374, 77,"Morning"),
    ("04/14/2026 6:32:00", 21, 77, 12357, 77,"Morning"),
    ("4/14/2026 13:28:00", 27.5, 65, 37850.0, 56, "Midday peak"),
    ("4/14/2026 13:28:30", 27.3, 64.5, 38000.0, 68, "Midday, Evaporative Cooler On"),
    ("4/14/2026 13:29:00", 27.2, 63.5, 37100, 69, "Midday"),
    ("4/14/2026 13:29:30", 27.1, 63.2, 37466, 72, "Midday"),
    ("4/14/2026 13:30:00", 26.9, 63.0, 37516, 83, "Midday"),
    ("4/14/2026 13:30:30", 26.6, 62.9, 37566, 84, "Midday"),
    ("4/14/2026 13:31:00", 26.5, 62.5, 37616, 82, "Midday"),
    ("4/14/2026 13:31:30", 26.5, 62.2, 37666, 82, "Midday"),
    ("4/14/2026 13:32:00", 26.3, 62, 37716, 81, "Midday"),
    ("4/14/2026 19:28:00", 25.3, 78.0, 3852.0, 67, "Evening"),
    ("4/14/2026 19:28:30", 25.0, 77.0, 3950.0, 74, "Evening"),
    ("4/14/2026 19:29:00", 24.9, 76.5, 5012, 76.0, "Evening"),
    ("4/14/2026 19:29:30", 24.5, 75.5, 4018.0, 79.0, "Evening"),
    ("04/14/2026 19:30", 24.1, 74, 4598, 81, "Evening"),
    ("4/14/2026 19:30:30", 24.0, 72.4, 4754.0, 85, "Evening"),
    ("4/14/2026 19:31:00", 24.0, 72.3, 4910.0, 85, "Evening"),
    ("4/14/2026 19:31:30", 23.8, 71.5, 5066, 84, "Evening"),
    ("4/14/2026 19:32:00", 23.5, 71.0, 4670, 84, "Evening"),
    ("04/15/2026 6:28:00", 17, 65, 11561, 63.0, "Morning - Cold"),
    ("04/15/2026 6:28:30", 17.9, 68, 12354, 67, "Morning- Cold"),
    ("04/15/2026 6:29:00", 18.6, 72, 13275, 72, "Morning - borderline"),
    ("04/15/2026 6:29:30", 19.9, 75, 12591, 73, "Morning"),
    ("04/15/2026 6:30:00", 22, 78, 12874, 75, "Morning"),
    ("04/15/2026 6:30:30", 22, 78, 11956, 75, "Morning"),
    ("04/15/2026 6:31:00", 22, 78.2, 13545, 74, "Morning"),
    ("04/15/2026 6:31:30", 22.1, 78.1, 12374, 74, "Morning"),
    ("04/15/2026 6:32:00", 22.1, 78, 12357, 74, "Morning"),
    ("4/15/2026 13:29:30", 28.5, 62.0, 37616.0, 84.0, "Midday"),
    ("04/15/2026 13:30:00", 27.4, 60.0, 37666, 83.0, "Midday"),
    ("4/15/2026 13:30:30", 26, 61, 37716, 81, "Midday"),
    ("4/15/2026 19:29:30", 25.3, 75.0, 4670, 80, "Evening"),
    ("4/15/2026 19:30:00", 24.7, 72.0, 5378, 81, "Evening"),
    ("4/15/2026 19:30:30", 24.5, 71, 5534, 79, "Evening"),
    ("4/16/2026 6:29:30", 22, 78, 12874, 75, "Morning"),
    ("04/16/2026 6:30:00", 22.5, 76, 11956, 74, "Morning"),
    ("4/16/2026 6:30:30", 22.6, 71, 13545, 72, "Morning"),
    ("4/16/2026 13:29:30", 30, 84, 37650, 49, "Midday, High Temp and Humidity"),
    ("04/16/2026 13:30:00", 28.1, 85, 36950, 58, "Midday, High Temp and Humidity"),
    ("4/16/2026 13:30:30", 26, 87, 34698, 67, "High humidity"),
    ("4/16/2026 19:29:30", 26, 72, 5739, 82, "Evening"),
    ("04/16/2026 19:30:00", 25.3, 70, 5378, 82, "Evening"),
    ("4/16/2026 19:30:30", 24.5, 63, 5534, 81, "Evening"),
    ("04/17/2026 6:29:30", 22.7, 78, 13545, 74, "Morning"),
    ("04/17/2026 6:30:00", 22.8, 75, 12374, 72, "Morning"),
    ("04/17/2026 6:30:30", 22.8, 73, 12357, 71, "Morning"),
    ("4/17/2026 13:29:30", 30, 52, 37650, 86, "VPD STRESS, 30°C + 52% RH → VPD ~1.82 kPa"),
    ("4/17/2026 13:30:00", 28.7, 55, 36950, 84, "Midday, High VPD"),
    ("4/17/2026 13:30:30", 27, 58.0, 34698, 84, "Midday, High VPD"),
    ("4/17/2026 19:29:30", 27, 68, 3852, 80, "Evening"),
    ("04/17/2026 19:30:00", 25.8, 69, 3950, 81, "Evening"),
    ("4/17/2026 19:30:30", 24.0, 67, 5012, 80, "Evening"),
    ("04/18/2026 6:29:30", 23.3, 67, 11561, 57, "Morning"),
    ("04/18/2026 6:30:00", 23.1, 65, 12354, 60, "Morning"),
    ("04/18/2026 6:30:30", 23.4, 64, 13275, 61, "Morning"),
    ("4/18/2026 13:29:30", 26.1, 56, 37466, 66, "Midday"),
    ("04/18/2026 13:30:00", 25.6, 55, 37516, 65, "Midday"),
    ("4/18/2026 13:30:30", 25, 53, 37566, 65.2, "Midday"),
    ("4/18/2026 19:29:30", 24.9, 70, 3950, 61.2, "Evening"),
    ("04/18/2026 19:30", 24.3, 68, 5012, 62, "Evening"),
    ("4/18/2026 19:30:30", 24.1, 65, 4018, 62, "Evening"),
    ("4/19/2026 0:11:41", 27.29, 71.0, 4598, 79.01, "Late night"),
    ("4/19/2026 0:13:10", 26.57, 74.3, 14.17, 80.5, "Late night, light sensor had an error"),
    ("4/19/2026 0:15:41", 26.57, 74.2, 14.17, 84, "Late night"),
    ("4/19/2026 0:18:42", 26.29, 74.5, 14.17, 85.03, "Late night"),
    ("4/19/2026 0:21:43", 26.21, 75.9, 14.17, 86.1, "Late night"),
    ("4/19/2026 0:24:47", 25.79, 77.5, 14.17, 86, "Late night"),
    ("4/19/2026 0:27:45", 25.64, 78.4, 14.17, 85.13, "Late night"),
    ("4/19/2026 0:29:06", 25.57, 82.4, 15.0, 86.94, "Late night — humidity rising"),
    ("4/19/2026 0:32:38", 25.14, 85.2, 15.0, 85.73, "Late night"),
    ("4/19/2026 0:39:05", 25.14, 84.8, 290.0, 85.59, "Late night"),
    ("4/19/2026 0:52:15", 25.14, 84.7, 585.0, 84.57, "Late night"),
    ("4/19/2026 0:59:13", 25.0, 84.0, 15.0, 85.63, "Late night"),
    ("4/19/2026 1:13:05", 24.86, 85.1, 15.0, 83.96, "Late night"),
    ("4/19/2026 1:35:25", 24.71, 85.8, 14.17, 84.25, "Late night — 0.14L water dispensed"),
    ("4/19/2026 1:39:23", 24.71, 86.5, 14.17, 83.54, "Late night"),
]

def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Scenario).first():
            print("Already Seeded")
            return
        scenario = Scenario(
            name= "Tomato Greenhouse",
            description=(
                "Sensor data from the IoT Smart Greenhouse prototype. "
                "Crop: cherry tomato (Solanum lycopersicum), seedling to fruiting stage. April 14–19 2026. "
                "Includes: cold morning (Apr 15), high-humidity Botrytis risk (Apr 16 midday), "
                "VPD stress (Apr 17 midday, 52% RH at 30°C), overnight session (Apr 19)."
            ),
        crop_type="tomato",
        location="Ismailia, Egypt",
        )
        db.add(scenario)
        db.flush()
        db.bulk_save_objects([
            Reading(
                scenario_id=scenario.id,
                timestamp=__parse_ts(row[0]),
                temperature_c=float(row[1]),
                humidity_pct=float(row[2]),
                light_lux=float(row[3]),
                soil_moisture_pct=float(row[4]),
                wind_speed_ms=0.5,
                notes=row[5],

            )
            for row in RAW_DATA
        ])
        db.commit()
        print(f"Seeded {len(RAW_DATA)} readings")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
if __name__ == "__main__":  # unindented, outside seed()
    seed()