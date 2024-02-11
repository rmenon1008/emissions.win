class PlaneStatus:
    def __init__(self, reg, lat, lon, alt, status, airport, timestamp):
        self.reg = reg
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.status = status
        self.airport = airport
        self.timestamp = timestamp

    def __repr__(self):
        return f"PlaneStatus({self.timestamp}: {self.reg}, {self.status})"

    def db_insert(self, conn):
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO plane_status VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                self.reg,
                self.lat,
                self.lon,
                self.alt,
                self.status,
                self.airport,
                self.timestamp,
            ),
        )
        conn.commit()


class Flight:
    def __init__(
        self,
        plane_reg,
        status_start_id,
        status_end_id,
    ):
        self.plane_reg = plane_reg
        self.status_start_id = status_start_id
        self.status_end_id = status_end_id

    def __repr__(self):
        return f"Flight({self.plane_reg}, {self.status_start_id}, {self.status_end_id})"

    def db_insert(self, conn):
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO flights VALUES (NULL, ?, ?, ?)
            """,
            (
                self.plane_reg,
                self.status_start_id,
                self.status_end_id,
            ),
        )
        conn.commit()
