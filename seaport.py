from plotableitem import PlotableItem
from node import Node


class Seaport(Node, PlotableItem):
    def __init__(
        self, id, name, lat, lon, country, svg="res/img/transport_marina.svg", scale=1.0
    ):
        Node.__init__(self, id, name, lat, lon, active=True)
        PlotableItem.__init__(self, id, name, lat, lon, svg, scale)

        self.country = country

    def getColor(self):
        return QColor(0, 100, 255)

    def getTooltip(self):
        return f"Port: {self.name}\nCountry: {self.country_name}\nID: {self.id}"

    @classmethod
    def fromDbRow(cls, row):
        return cls(
            id=row["id"],
            name=row["name"],
            lat=row["latitude"],
            lon=row["longitude"],
            country_name=row["country_name"],
            active=bool(row.get("active", True)),
        )
