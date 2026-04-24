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
        size=15.0,
    ):
        DBItem.__init__(self, id, name, wkb_geometry)
        PlotableItem.__init__(self, id, name, wkb_geometry, img, size)

        self.country = country

    def getColor(self):
        return QColor(0, 100, 255)

    def getTooltip(self):
        return f"Port: {self.name}\nCountry: {self.country}\nID: {self.id}"

    @classmethod
    def fromDbRow(cls, row):
        item_id = row["seaport_id"]
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
            name=row.get("seaport_name"),
            wkb_geometry=wkb_bytes,
            country=row.get("country_name"),
        )

    @classmethod
    def sqlQuery(cls, min_lon, min_lat, max_lon, max_lat):
        query_str = """
            SELECT seaport_id, seaport_name, wkb_geometry, country_name
            FROM seaports s
            JOIN countries c ON s.country_id = c.country_id
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
                    print(f"Error while parsing item {row["seaport_id"]}: {e}")

        return True, new_items
