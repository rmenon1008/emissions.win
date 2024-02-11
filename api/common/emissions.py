import json

PLANES = json.load(open("data/planes.json"))
ENGINES = json.load(open("data/engines.json"))

LTO_DURATION_S = 32.7 * 60  # 32.7 minutes
CO2_KG_PER_FUEL_KG = 3.16


def estimate_fuel_usage(flight_details, plane_reg):
    if plane_reg not in PLANES:
        raise ValueError(f"Unknown plane: {plane_reg}")

    plane = PLANES[plane_reg]
    engine_count = plane["engine_count"]
    engine_model = plane["engine_model"]

    if engine_model not in ENGINES:
        raise ValueError(f"Unknown engine model: {engine_model}")

    full_lto_kg = ENGINES[engine_model]["full_lto_kg"]
    cruise_kg_s = ENGINES[engine_model]["cruise_kg_s"]

    remaining_airtime_s = max(flight_details["airtime_s"] - LTO_DURATION_S, 0)
    fuel_used_kg = (full_lto_kg + remaining_airtime_s * cruise_kg_s) * engine_count

    return fuel_used_kg


def emissions_from_fuel_usage(fuel_used_kg):
    return fuel_used_kg * CO2_KG_PER_FUEL_KG


def carbon_capture_cost(emissions_kg):
    return emissions_kg * 100
