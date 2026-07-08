# Osmoviz

[Live Demo](http://localhost:8000) — run locally, no hosted version yet

Built this project using sensor data from my school's IoT greenhouse prototype. The idea was to take the raw numbers the greenhouse was logging and actually do something useful with them like calculating plant stress, visualizing it, and showing which environmental parameter is causing the most damage at any given reading.

## What it does

Takes sensor readings (air temp, humidity, soil moisture, light intensity) from a cherry tomato greenhouse and runs them through the FAO-56 Penman-Monteith evapotranspiration formula to compute ET₀ and ETc. Then calculates 8 individual stress indices (heat, chilling, VPD high/low, light high/low, waterlogging, wilting) and shows everything on a dashboard with a tomato SVG that reacts by changing leaf color, stem color, and root color depending on what stress is dominant.

## What it's built with

- Python FastAPI for the backend
- SQLite for storing scenarios and readings
- Vanilla JS + Chart.js for the frontend
- Custom SVG tomato plant (hand-coded paths)
- FAO-56 Penman-Monteith implemented from scratch in Python
- Sensor data from the greenhouse in April

## Running it

```bash
pip install -r requirements.txt
python -m backend.seed_data
uvicorn backend.main:app --reload --port 8000
```

open `http://localhost:8000`  
API docs at `http://localhost:8000/api/docs`

## The data

84 real readings from April 14–19 2026. Five stress events are in there: a cold morning startup at 17°C, a Botrytis risk day where humidity hit 87% at midday, a VPD crisis where humidity dropped to 52% at 30°C pushing VPD to ~1.82 kPa, an overnight session where soil moisture hit 100% for almost 90 minutes straight, and a combined cold + high humidity night at 16.3°C and 92.3% RH.

## What I learned

- FastAPI and SQLAlchemy work really well together but took some getting used to
- Chart.js has a plugin system that isn't very well documented
- SVG paths for the plant were all done manually with Bezier curves. Took a while to get the leaves and roots looking right

## The greenhouse project this is based on

The data comes from a prototype I built at Ismailia STEM High School in Egypt. The prototype had an ESP32 microcontroller, DHT-22 for air temp and humidity, BH-1750 for light, DS18B20 for soil temp, a soil moisture sensor, MQ-135 for air quality, and a water flow sensor. It controlled fans, pumps, a Peltier element, and grow lights through a relay board. The prototype itself is probably disassembled by now but the data lives on here.
