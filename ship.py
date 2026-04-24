<<<<<<< HEAD
from PySide6.QtGui import QColor

from plotableitem import PlotableItem
from dbitem import DBItem
=======
from plotableitem import PlotableItem
from dbitem import DBItem
from PySide6.QtGui import QColor
>>>>>>> a4a8dd7 (Initial version of the map viewer)


class Ship(DBItem, PlotableItem):
    """Navire en mouvement"""

<<<<<<< HEAD
    def __init__(self, id, name, wkb_geometry, heading, capacity, desc, ship_type):
        DBItem.__init__(self, id, name, wkb_geometry)
        PlotableItem.__init__(
            self, id, name, wkb_geometry, img="res/img/ferry32.png", size=30.0
        )

        # id = imo
=======
    def __init__(self, imo, mmsi, name, lat, lon, heading, capacity, desc, ship_type):
        super(DBItem, self).__init__(imo, name, lat, lon)
        super(PlotableItem, self).__init__(
            imo, name, lat, lon, svg="res/img/Arrow_05.svg", scale=0.4
        )

        self.mmsi = mmsi
>>>>>>> a4a8dd7 (Initial version of the map viewer)
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
<<<<<<< HEAD
        item_id = row["imo"]
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
            id=item_id,
            name="",
            wkb_geometry=wkb_bytes,
=======
        return cls(
            id=row["imo"],
            mmsi=row["mmsi"],
            name=row["name"],
            lat=row["latitude"],
            lon=row["longitude"],
>>>>>>> a4a8dd7 (Initial version of the map viewer)
            heading=row.get("heading"),
            capacity=row["capacity"],
            desc=row.get("description", ""),
            ship_type=row["type"],
        )
<<<<<<< HEAD

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
                    print(f"Error while parsing item {row["imo"]}: {e}")

        return True, new_items
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
