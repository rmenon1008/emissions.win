import base64
import io
import math

import PIL.Image
from common.emissions import (
    carbon_capture_cost,
    emissions_from_fuel_usage,
    estimate_fuel_usage,
)


def get_flight(cursor, flight_id):
    cursor.execute(
        """
        SELECT flights.id, flights.plane_reg, flights.status_start_id, flights.status_end_id, plane_status.status
        FROM flights
        JOIN plane_status ON flights.status_start_id = plane_status.id
        WHERE flights.id = ?
    """,
        (flight_id,),
    )
    flight = cursor.fetchone()
    if flight is None:
        return None

    status_start_id = flight[2]
    status_end_id = flight[3]

    cursor.execute(
        """
        SELECT id, reg, lat, lon, alt, status, airport, time
        FROM plane_status
        WHERE id >= ?
        AND id <= ?
    """,
        (status_start_id, status_end_id),
    )
    statuses = cursor.fetchall()
    waypoints = []
    for status in statuses:
        waypoints.append(
            {
                "lat": status[2],
                "lon": status[3],
                "alt": status[4],
                "status": status[5],
                "airport": status[6],
                "time": status[7],
            }
        )

    duration_s = waypoints[-1]["time"] - waypoints[0]["time"]
    distance_km = distance_from_waypoints(waypoints)
    fuel_used_kg = estimate_fuel_usage(
        {"airtime_s": duration_s, "distance_km": distance_km}, flight[1]
    )
    emissions_kg = emissions_from_fuel_usage(fuel_used_kg)
    capture_cost_usd = carbon_capture_cost(emissions_kg)

    return {
        "id": flight[0],
        "plane_reg": flight[1],
        "starting_airport": waypoints[0]["airport"],
        "starting_time": waypoints[0]["time"],
        "ending_airport": waypoints[-1]["airport"],
        "ending_time": waypoints[-1]["time"],
        "duration_s": waypoints[-1]["time"] - waypoints[0]["time"],
        "distance_km": distance_km,
        "fuel_used_kg": fuel_used_kg,
        "emissions_kg": emissions_kg,
        "carbon_capture_cost_usd": capture_cost_usd,
        "waypoints": waypoints,
    }


def distance_from_waypoints(waypoints):
    distance_km = 0
    for i in range(len(waypoints) - 1):
        distance_km += haversine(
            waypoints[i]["lat"],
            waypoints[i]["lon"],
            waypoints[i + 1]["lat"],
            waypoints[i + 1]["lon"],
        )
    return distance_km


def haversine(lat1, lon1, lat2, lon2):
    # https://stackoverflow.com/a/4913653/170656
    R = 6372.8  # Earth radius in kilometers

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat / 2) ** 2 + math.sin(dLon / 2) ** 2 * math.cos(lat1) * math.cos(
        lat2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c
