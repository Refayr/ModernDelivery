from dbitem import DBItem


class Node(DBItem):
    """Représente un point géographique (Port, Carrefour, etc.)"""

    def __init__(self, id, name, lat, lon, active=True):
        super().__init__(id, name or f"Node {id}", lat, lon)
        self.active = active
        self.connections = []

    @classmethod
    def fromDbRow(cls, row):
        return cls(
            id=row["id"],
            name=row.get("name"),  # Peut venir d'une jointure ou être NULL
            lat=row["latitude"],
            lon=row["longitude"],
            active=bool(row.get("active", True)),
        )
