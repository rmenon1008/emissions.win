import json
import sqlite3
import time

import flask
import flask_cors
from common.helpers import get_flight

INDEX = json.load(open("data/index.json"))


def run_server(port=8080):
    app = flask.Flask(__name__)
    flask_cors.CORS(app)

    @app.route("/api/v1/get_people")
    def get_people_route():
        people = INDEX["people"]
        conn = sqlite3.connect("flight_tracking.db")
        cursor = conn.cursor()

        max_age_days = flask.request.args.get("maxAgeDays", default=0, type=int)

        output = []

        for person in people:
            total_emissions_kg = 0
            total_flight_count = 0
            total_flight_distance_km = 0
            total_flight_duration_s = 0
            flights = []
            for plane in person["planes"]:
                plane_name = plane["name"]
                cursor.execute(
                    """
                    SELECT id
                    FROM flights
                    WHERE plane_reg = ?
                """,
                    (plane["reg"],),
                )
                flight_entries = cursor.fetchall()
                total_flight_count += len(flight_entries)
                for flight in flight_entries:
                    flight = get_flight(cursor, flight[0])
                    if flight is None:
                        continue
                    if max_age_days > 0:
                        if (
                            time.time() - flight["starting_time"]
                            > max_age_days * 24 * 60 * 60
                        ):
                            continue
                    flights.append(flight)
                    total_emissions_kg += flight["emissions_kg"]
                    total_flight_distance_km += flight["distance_km"]
                    total_flight_duration_s += flight["duration_s"]

            output.append(
                {
                    "name": person["name"],
                    "image": person["image"],
                    "flights": [
                        {
                            "id": flight["id"],
                            "reg": flight["plane_reg"],
                            "plane_name": plane_name,
                            "emissions_kg": flight["emissions_kg"],
                            "distance_km": flight["distance_km"],
                            "duration_s": flight["duration_s"],
                            "starting_airport": flight["starting_airport"],
                            "ending_airport": flight["ending_airport"],
                            "starting_time": flight["starting_time"],
                            "ending_time": flight["ending_time"],
                        }
                        for flight in flights
                    ],
                    "total_emissions_kg": total_emissions_kg,
                    "total_flight_count": total_flight_count,
                    "total_flight_distance_km": total_flight_distance_km,
                    "total_flight_duration_s": total_flight_duration_s,
                }
            )

        conn.close()
        return flask.jsonify(output)

    @app.route("/api/v1/get_flight/<int:flight_id>")
    def get_flight_route(flight_id):
        conn = sqlite3.connect("flight_tracking.db")
        flight = get_flight(conn.cursor(), flight_id)
        conn.close()
        return flask.jsonify(flight)

    @app.route("/api/mock/get_flight/<int:flight_id>")
    def get_flight_route_mock(flight_id):
        conn = sqlite3.connect("flight_tracking.db")
        flight = get_flight(conn.cursor(), flight_id)
        conn.close()
        return flask.jsonify(flight)

    @app.route("/api/mock/get_people")
    def get_mock_people_route():
        return flask.jsonify(json.load(open("data/mock_people.json")))

    @app.route("/static/<path:path>")
    def static_route(path):
        return flask.send_from_directory("static", path)

    app.run(host="localhost", port=port, debug=True)
