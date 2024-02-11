import json
import logging
import sqlite3
import time
from datetime import datetime, timezone

import requests
from common.classes import PlaneStatus

INDEX = json.load(open("data/index.json"))
AIRPORTS = json.load(open("data/airports.json"))

logging.basicConfig(level=logging.INFO)


def close_to_airport(latitude, longitude):
    for airport in AIRPORTS.values():
        if (
            abs(latitude - airport["lat"]) < 0.05
            and abs(longitude - airport["lon"]) < 0.05
        ):
            return airport
    return None


def get_plane_status(reg):
    logging.info(f"  Updating {reg}")
    url = f"https://adsbexchange-com1.p.rapidapi.com/v2/registration/{reg}/"
    headers = {
        "X-RapidAPI-Key": "d51f57a912mshdcfd721cb1cf960p13315ejsnf8688c269dd5",
        "X-RapidAPI-Host": "adsbexchange-com1.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Error: {response.status_code}")
        return None
    location_response = response.json()
    timestamp = datetime.now(timezone.utc).timestamp()

    if len(location_response["ac"]) == 0:
        return PlaneStatus(reg, None, None, None, "unknown", None, timestamp)
    else:
        lat = location_response["ac"][0]["lat"]
        lon = location_response["ac"][0]["lon"]
        alt = location_response["ac"][0]["alt_baro"]
        print(lat, lon, alt)

        airport = close_to_airport(lat, lon)
        if airport is not None:
            if alt == "ground" or abs(alt - airport["elevation"]) < 250:
                return PlaneStatus(
                    reg, lat, lon, alt, "ground", airport["icao"], timestamp
                )
            else:
                return PlaneStatus(reg, lat, lon, alt, "flying", None, timestamp)
        else:
            return PlaneStatus(reg, lat, lon, alt, "flying", None, timestamp)


def set_up_db():
    conn = sqlite3.connect("flight_tracking.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS plane_status (
            id integer primary key autoincrement,
            reg text,
            lat real,
            lon real,
            alt real,
            status text,
            airport text,
            time integer,
            flight_id integer
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS flights (
            id integer primary key autoincrement,
            plane_reg text,
            status_start_id integer,
            status_end_id integer
        )
    """
    )
    conn.commit()
    return conn


def does_plane_need_update(last_status):
    # Decides whether a plane needs to be updated
    # If the plane is flying, update every 1 minute
    # If the plane is on the ground, update every 10 minutes
    # If the plane is unknown, update every 10 minutes

    if last_status.status == "unknown":
        update_time = 60 * 10  # 10 minutes
    elif last_status.status == "ground":
        update_time = 60 * 5  # 5 minutes
    else:
        update_time = 60 * 3  # 3 minutes

    needs_update = (
        datetime.now(timezone.utc).timestamp() - last_status.timestamp > update_time
    )
    return needs_update


def update_loop():
    conn = set_up_db()
    last_plane_statuses = {}

    while True:
        for person in INDEX["people"]:
            logging.info(f"Updating {person['name']}")
            for plane in person["planes"]:
                if plane["reg"] in last_plane_statuses:
                    last_status = last_plane_statuses[plane["reg"]]
                    needs_update = does_plane_need_update(last_status)
                    if not needs_update:
                        logging.info(f"  Skipping {plane['reg']}")
                        continue

                reg = plane["reg"]
                status = get_plane_status(reg)
                if status is None:
                    continue

                last_plane_statuses[reg] = status
                status.db_insert(conn)
                logging.info(f"    Status: {status}")

        for person in INDEX["people"]:
            for plane in person["planes"]:
                reg = plane["reg"]

                # Get all the rows for this plane with no flight_id
                c = conn.cursor()
                c.execute(
                    """
                    SELECT * FROM plane_status
                    WHERE reg = ?
                    AND flight_id IS NULL
                    ORDER BY time ASC
                    """,
                    (reg,),
                )
                rows = c.fetchall()

                # If there are no rows, skip
                if len(rows) == 0:
                    continue

                # Find the first and last ground rows (there may be many in a row)
                first_ground = None
                last_ground = None
                for i, row in enumerate(rows):
                    if row[5] == "ground":
                        first_ground = i
                        break
                for i, row in enumerate(reversed(rows)):
                    if row[5] == "ground":
                        last_ground = len(rows) - i - 1
                        break

                if first_ground is None or last_ground is None:
                    continue

                rows_between_LTO = rows[first_ground : last_ground + 1]

                if len(rows_between_LTO) < 5:
                    continue

                # Filter out rows with status "unknown"
                in_flight_rows = [
                    row for row in rows_between_LTO if row[5] != "unknown"
                ]

                # Find the biggest timestamp gap between flying rows in the in-flight rows
                biggest_gap = 0
                for i in range(len(in_flight_rows) - 1):
                    gap = in_flight_rows[i + 1][7] - in_flight_rows[i][7]
                    if gap > biggest_gap:
                        biggest_gap = gap

                # If the biggest gap is more than 20 minutes, skip
                if biggest_gap > 60 * 20:
                    continue

                # Insert a new flight
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO flights VALUES (NULL, ?, ?, ?)
                    """,
                    (reg, rows_between_LTO[0][0], rows_between_LTO[-1][0]),
                )
                conn.commit()

                # Get the flight_id
                c = conn.cursor()
                c.execute(
                    """
                    SELECT id FROM flights
                    WHERE plane_reg = ?
                    AND status_start_id = ?
                    AND status_end_id = ?
                    """,
                    (reg, rows_between_LTO[0][0], rows_between_LTO[-1][0]),
                )
                flight_id = c.fetchone()[0]

                # Update the rows with the flight_id
                c = conn.cursor()
                c.execute(
                    """
                    UPDATE plane_status
                    SET flight_id = ?
                    WHERE reg = ?
                    AND time >= ?
                    AND time <= ?
                    """,
                    (
                        flight_id,
                        reg,
                        rows[0][7],
                        rows[-1][7],
                    ),
                )

        time.sleep(60)
