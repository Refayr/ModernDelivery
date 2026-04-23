from plotableitem import PlotableItem
from dbitem import DBItem
from PySide6.QtGui import QColor


class Ship(DBItem, PlotableItem):
    """Navire en mouvement"""

    def __init__(self, id, name, wkb_geometry, heading, capacity, desc, ship_type):
        DBItem.__init__(self, id, name, wkb_geometry)
        PlotableItem.__init__(
            self, id, name, wkb_geometry, svg="res/img/ferry_terminal.svg", scale=500.0
        )

        # id = imo
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
        wkb_data = row.get("wkb_geometry")
        wkb_bytes = None

        if isinstance(wkb_data, bytes):
            wkb_bytes = wkb_data

        elif hasattr(wkb_data, "data"):
            wkb_bytes = bytes(wkb_data)

        elif isinstance(wkb_data, str):
            try:
                wkb_bytes = bytes.fromhex(wkb_data)
            except ValueError:
                print(
                    f"⚠️ Format inattendu pour wkb_geometry de l'item {item_id}: {type(wkb_data)}"
                )
                wkb_bytes = None

        elif wkb_data is None or wkb_data == "":
            wkb_bytes = None

        else:
            try:
                wkb_bytes = bytes(wkb_data)
            except Exception as e:
                print(f"⚠️ Impossible de convertir wkb_geometry pour {item_id}: {e}")
                wkb_bytes = None

        return cls(
            id=row["imo"],
            name="",
            wkb_geometry=wkb_bytes,
            heading=row.get("heading"),
            capacity=row["capacity"],
            desc=row.get("description", ""),
            ship_type=row["type"],
        )

    @classmethod
    def sqlQuery(cls, min_lon, min_lat, max_lon, max_lat):
        query_str = """
            SELECT imo, wkb_geometry, heading, capacity, description, type
            FROM ships
            WHERE ST_Intersects(
                wkb_geometry,
                ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
            )
        """

        return query_str, (min_lon, min_lat, max_lon, max_lat)

    @classmethod
    def loadVisibleItemsFromDb(cls, db_connector, min_lon, min_lat, max_lon, max_lat):
        """
        Charge les Ships, Seaports, Nodes et Connections dans la zone visible.
        Remplace les données existantes uniquement pour ces types dans cette zone.
        """
        if not db_connector.isConnected():
            return False, 0

        query, values = cls.sqlQuery(min_lon, min_lat, max_lon, max_lat)

        total_count = 0

        success, results = db_connector.executeQuery(query, values)

        new_items = []
        if not success:
            print(f"⚠️ Loadind error Ships: {results}")
        else:
            for row in results:
                try:
                    item = Ship.fromDbRow(row)

                    new_items.append(item)
                except Exception as e:
                    print(f"Error while parsing item {item_id}: {e}")

            # Debug optionnel
            # print(f"✅ {item_type}: {len(new_items)} items chargés (zone visible)")

        return True, new_items
