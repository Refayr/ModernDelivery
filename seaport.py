<<<<<<< HEAD
from PySide6.QtGui import QColor

from plotableitem import PlotableItem
from dbitem import DBItem


class Seaport(DBItem, PlotableItem):
    def __init__(
        self,
        id,
        name,
        wkb_geometry,
        country,
        img="res/img/marina32.png",
        size=30.0,
    ):
        DBItem.__init__(self, id, name, wkb_geometry)
        PlotableItem.__init__(self, id, name, wkb_geometry, img, size)
=======
from plotableitem import PlotableItem
from node import Node


class Seaport(Node, PlotableItem):
    def __init__(
        self, id, name, lat, lon, country, svg="res/img/transport_marina.svg", scale=1.0
    ):
        super(Node, self).__init__(id, name, lat, lon, active=True)
        super(PlotableItem, self).__init__(id, name, lat, lon, svg, scale)
>>>>>>> a4a8dd7 (Initial version of the map viewer)

        self.country = country

    def getColor(self):
        return QColor(0, 100, 255)

    def getTooltip(self):
<<<<<<< HEAD
        return f"Port: {self.name}\nCountry: {self.country}\nID: {self.id}"

    @classmethod
    def fromDbRow(cls, row):
        item_id = row["id"]
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
                    f"⚠️ Unexpected format for wkb_geometry item {item_id}: {type(wkb_data)}"
                )
                wkb_bytes = None

        elif wkb_data is None or wkb_data == "":
            wkb_bytes = None

        else:
            try:
                wkb_bytes = bytes(wkb_data)
            except Exception as e:
                print(f"⚠️ Impossible to convert wkb_geometry for item {item_id}: {e}")
                wkb_bytes = None

        return cls(
            id=item_id,
            name=row.get("name"),
            wkb_geometry=wkb_bytes,
            country=row.get("country"),
        )

    @classmethod
    def sqlQuery(cls, min_lon, min_lat, max_lon, max_lat):
        query_str = """
            SELECT s.id, s.name, wkb_geometry, country, active
            FROM seaports s
            JOIN nodes n ON node = n.ogc_fid
            JOIN countries c ON country = c.id
            WHERE n.active = true
            AND ST_Intersects(
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
            print(f"⚠️ Loadind error Seaports: {results}")
        else:
            for row in results:
                try:
                    item = Seaport.fromDbRow(row)

                    new_items.append(item)
                except Exception as e:
                    print(f"Error while parsing item {row["id"]}: {e}")

        return True, new_items
=======
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
>>>>>>> a4a8dd7 (Initial version of the map viewer)
