from plotableitem import PlotableItem
from dbitem import DBItem
from PySide6.QtGui import QColor


class Ship(DBItem, PlotableItem):
    """Navire en mouvement"""

    def __init__(self, imo, mmsi, name, lat, lon, heading, capacity, desc, ship_type):
        super(DBItem, self).__init__(imo, name, lat, lon)
        super(PlotableItem, self).__init__(
            imo, name, lat, lon, svg="res/img/Arrow_05.svg", scale=0.4
        )

        self.mmsi = mmsi
        self.heading = heading  # ID du port de destination ou None
        self.capacity = capacity
        self.description = desc
        self.type = ship_type

    def currentLoad(self):
        # TODO
        return 0

    def getColor(self):
        return QColor(0, 200, 0)  # Vert pour les navires

    def getTooltip(self):
        status = "Anchored"
        if self.heading:
            status = f"Heading to Seaport ID: {self.heading}"

        return (
            f"Ship: {self.name}\nIMO: {self.id}\nType: {self.type}\n"
            f"Capacity: {self.currentLoad()}/{self.capacity}t\nStatut: {status}"
        )

    @classmethod
    def fromDbRow(cls, row):
        return cls(
            id=row["imo"],
            mmsi=row["mmsi"],
            name=row["name"],
            lat=row["latitude"],
            lon=row["longitude"],
            heading=row.get("heading"),
            capacity=row["capacity"],
            desc=row.get("description", ""),
            ship_type=row["type"],
        )
