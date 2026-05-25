from __future__ import annotations
import math
from dataclasses import dataclass


def saturation_vapor_pressure(T: float) -> float:
    return 0.6108 * math.exp(17.27 * T / (T + 237.3))

def vapor_pressure_deficit(T: float, RH: float) -> float:
    es = saturation_vapor_pressure(T)
    ea = es * (RH / 100.0)
    return max(0.0, es - ea)

def slope_svp_curve(T: float) -> float:
    return (4098.0 * saturation_vapor_pressure(T)) / ((T + 237.3) ** 2)

def atmospheric_pressure(elevation_m: float) -> float:
    return 101.3 * ((293.0 - 0.0065 * elevation_m) / 293.0) ** 5.26



def psychrometric_constant(elevation_m: float) -> float:
    return 0.000665 * atmospheric_pressure(elevation_m)
def lux_to_solar_radiation(lux: float) -> float:
    return (lux / 93.0) * 0.0036

def extraterrestrial_radiation_hourly(
    latitude_deg: float,day_of_year: int,hour: int,
    longitude_deg: float = 32.27,standard_meridian_deg: float = 30.0,
) -> float:
    GSC = 0.0820
    phi  =  math.radians(latitude_deg)
    dr = 1.0 + 0.033 * math.cos(2.0 * math.pi  * day_of_year / 365.0)
    delta = 0.409 * math.sin(2.0 *math.pi * day_of_year / 365.0 - 1.39)
    b = 2.0 * math.pi * (day_of_year - 81) / 364.0
    Sc = 0.1645 * math.sin(2.0 *b) - 0.1255 * math.cos(b) - 0.025 *math.sin(b)
    omega = (math.pi / 12.0) * (hour + 0.5 + 0.06667 * (standard_meridian_deg -longitude_deg) + Sc - 12.0)
    omega1 = omega- math.pi / 24.0
    omega2 =  omega + math.pi / 24.0
    omega_s = math.acos(max(-1.0, min(1.0,-math.tan(phi) * math.tan(delta))))
    omega1 = max(omega1, -omega_s)
    omega2 = min(omega2,   omega_s)


    if omega2 <= omega1:
        return 0.0
    Ra = (12.0 / math.pi) * GSC * dr * (
        (omega2 - omega1) * math.sin(phi) * math.sin(delta)
        + math.cos(phi) * math.cos(delta) * (math.sin(omega2) - math.sin(omega1)))
    return max(0.0, Ra)


def net_longwave_radiation(T: float, ea: float, Rs: float, Rso: float) -> float:
    Tk = T + 273.16
    humidity_factor = 0.34 - 0.14 * math.sqrt(max(ea, 0.001))
    if Rso > 1e-4:
        cloud_factor = max(0.05, min(1.0, 1.35 * (Rs / Rso) - 0.35))
    else:
        cloud_factor = 1.0
    return 2.042e-10 * (Tk ** 4) * humidity_factor * cloud_factor


def compute_net_radiation_minus_G(T: float, ea: float, Rs: float, Rso: float) -> float:
    Rns = (1.0 - 0.23) * Rs
    Rnl = net_longwave_radiation(T, ea, Rs, Rso)
    Rn = Rns - Rnl
    G = 0.10 * Rn if Rs > 0.05 else 0.50 * Rn
    return Rn - G


def eto_penman_monteith(
    T: float,
    RH: float,
    lux: float,
    wind_speed_ms: float,
    elevation_m: float = 10.0,
    latitude_deg: float = 30.60,
    day_of_year: int = 105,
    hour: int = 12,
    longitude_deg: float = 32.27,
) -> float:
    es = saturation_vapor_pressure(T)
    ea = es * (RH / 100.0)
    Delta = slope_svp_curve(T)
    gamma = psychrometric_constant(elevation_m)
    u2 = max(wind_speed_ms, 0.5)
    Rs = lux_to_solar_radiation(lux)
    Ra = extraterrestrial_radiation_hourly(latitude_deg, day_of_year, hour, longitude_deg)
    Rso = (0.75 + 2e-5 * elevation_m) * Ra
    RnG = compute_net_radiation_minus_G(T, ea, Rs, Rso)
    numerator = 0.408 * Delta * RnG + gamma * (37.0 / (T + 273.0)) * u2 * (es - ea)
    denominator = Delta + gamma * (1.0 + 0.34 * u2)

    return max(0.0, numerator / denominator)


_T = {
    "temp_heat_1": 28.0,"temp_heat_3": 38.0,
    "temp_chill_1": 15.0, "temp_chill_3": 8.0,
    "vpd_hi_1": 1.50,"vpd_hi_3": 2.50,
    "vpd_lo_1": 0.40,"vpd_lo_3": 0.15,
    "lux_hi_1": 70_000,"lux_hi_3": 110_000,
    "lux_lo_1": 15_000,"lux_lo_3": 2_000,
    "soil_wet_1": 85.0,"soil_wet_3": 95.0,
    "soil_dry_1": 40.0,
    "soil_dry_3": 20.0,
}

_WEIGHTS = {
    "heat": 0.18, "chilling": 0.12, "vpd_high": 0.18, "vpd_low": 0.08,
    "light_high": 0.08, "light_low": 0.10, "waterlogging": 0.12, "wilting": 0.14,
}

_RECS = {
    "optimal":      ["Conditions are ideal — maintain current management.", "Log this as a healthy baseline."],
    "heat":         ["Activate evaporative cooling: Fan 1+2 ON + Pump 2 (cellulose pad).","Activate Peltier cooling: Fan 3 ON + Pump 1 (soil pipes).","Increase irrigation frequency — smaller doses, more often (Pump 3)."],
    "chilling":     ["Activate Peltier heating: Fan 3 ON + Pump 1 (circulate warm water through soil pipes).",
                     "Switch off evaporative cooling: Pump 2 OFF + Fan 1+2 OFF.","Monitor for chilling-induced tip burn on young leaves."],
    "vpd_high":     ["Activate evaporative cooling: Fan 1+2 ON + Pump 2 (cellulose pad).","Reduce ventilation rate to slow moisture loss.",
                     "Check soil moisture — plants may need urgent irrigation (Pump 3)."],
    "vpd_low":      ["Increase ventilation: Fan 1+2 ON to lower humidity.",
                     "Turn off evaporative cooling: Pump 2 OFF.","Monitor for Botrytis cinerea on flowers and fruit.","Ensure adequate calcium — low VPD impairs Ca²⁺ uptake."],
    "light_high": [
        "Reduce grow light intensity or duty cycle.","Check leaves for bleaching or interveinal chlorosis.",
        "Increase irrigation to compensate for higher transpiration (Pump 3).","Consider repositioning grow lights further from the canopy.",
    ],
    "light_low": [
        "Activate grow lights: 20 red LEDs + 5 blue LEDs (80:20 ratio).",
        "Clean polycarbonate dome panels.","Consider CO₂ enrichment to maximise low-light photosynthesis.",],
    "waterlogging": ["Stop irrigation immediately — Pump 3 OFF.",
                     "Check drip lines and emitters for blockages.",
                     "Aerate root zone if possible.",
                     "Monitor roots for hypoxia / Phytophthora within 24–48h."],
    "wilting":      ["Irrigate immediately — Pump 3 ON.",
                     "Check soil moisture sensor calibration.",
                     "Inspect drip lines for blockages.",
                     "Shade dome temporarily to cut transpiration load."],
}


def _stress(value: float, onset: float, maximum: float, direction: str = "high") -> float:
    if direction == "high":
        if value <= onset: return 0.0
        if value >= maximum: return 1.0
        return (value - onset) / (maximum - onset)
    else:
        if value >= onset: return 0.0
        if value <= maximum: return 1.0
        return (onset - value) / (onset - maximum)


@dataclass
class StressResult:
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
    overall_stress:float
    dominant_stress:str
    stress_level:str
    active_stresses:list[str]
    recommendations:list[str]


def compute_stress_indices(
    T: float,
    RH: float,

    lux: float,
    soil_moisture_pct: float,
    wind_speed_ms: float = 0.5,
    elevation_m: float = 10.0,
    latitude_deg: float = 30.60,
    day_of_year: int = 105,
    hour: int = 12,
    longitude_deg: float = 32.27,) -> StressResult:

    vpd = vapor_pressure_deficit(T, RH)
    eto = eto_penman_monteith(T, RH, lux, wind_speed_ms, elevation_m, latitude_deg, day_of_year, hour, longitude_deg)
    etc = eto * 1.15 * 0.8
    raw = {
        "heat":_stress(T,_T["temp_heat_1"],  _T["temp_heat_3"],  "high"), "chilling":_stress(T,_T["temp_chill_1"], _T["temp_chill_3"], "low"),"vpd_high":_stress(vpd,_T["vpd_hi_1"],_T["vpd_hi_3"],"high"),
        "vpd_low":_stress(vpd,_T["vpd_lo_1"],_T["vpd_lo_3"],"low"),"light_high":_stress(lux,_T["lux_hi_1"],_T["lux_hi_3"],"high"),
        "light_low":_stress(lux,_T["lux_lo_1"],_T["lux_lo_3"],"low"),"waterlogging": _stress(soil_moisture_pct, _T["soil_wet_1"],_T["soil_wet_3"],"high"),
        "wilting":_stress(soil_moisture_pct, _T["soil_dry_1"],_T["soil_dry_3"],   "low"),
    }

    overall  = sum(v * _WEIGHTS[k] for k, v in raw.items()) * 100.0
    dominant = max(raw, key=raw.__getitem__)
    if raw[dominant] < 0.05:
        dominant = "optimal"

    active = [k for k, v in raw.items() if v > 0.15]

    if overall < 10.0:   level =   "optimal"
    elif overall < 30.0: level =  "mild"
    elif overall < 55.0: level =  "moderate"
    else:                level = "severe"
    recs = list(_RECS["optimal"]) if not active else []
    for s in sorted(active, key=lambda k: raw[k], reverse=True)[:2]:
        recs.extend(_RECS.get(s, []))
    return StressResult(
        vpd_kpa=round(vpd,4),
        eto_mm_h=round(eto, 4),
        etc_mm_h=round(etc,4),
        heat_stress=round(raw["heat"], 4),
        chilling_stress=round(raw["chilling"], 4),
        vpd_high_stress=round(raw["vpd_high"], 4),
        vpd_low_stress=round(raw["vpd_low"], 4),
        light_high_stress=round(raw["light_high"], 4),
        light_low_stress=round(raw["light_low"], 4),
        waterlogging_stress=round(raw["waterlogging"], 4),
        wilting_stress=round(raw["wilting"], 4),
        overall_stress=round(overall, 2),
        dominant_stress=dominant,
        stress_level=level,
        active_stresses=active,
        recommendations=recs,
    )