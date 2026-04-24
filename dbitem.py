import csv
from abstractitem import AbstractItem


class DBItem(AbstractItem):
    """Item from PostGIS or CSV file"""

<<<<<<< HEAD
    def __init__(self, id, name, wkb_geometry):
        super().__init__(id, name, wkb_geometry)
=======
    def __init__(self, id, name, lat, lon):
        super().__init__(id, name, lat, lon)

    @classmethod
    def fromCsvRow(cls, row):
        """Create an item from a CSV row"""
        lat = cls.parse_coordinate(row.get("latitude", ""))
        lon = cls.parse_coordinate(row.get("longitude", ""))

        return cls(
            id=row.get("id", ""),
            name=row.get("name", ""),
            lat=lat,
            lon=lon,
        )
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    @classmethod
    def fromDbRow(cls, row):
        """Create an item from PostGIS"""
        return cls(
            id=row.get("id", ""),
            name=row.get("name", ""),
<<<<<<< HEAD
            wkb_geometry=row.get("wkb_geometry"),
        )

    def sqlQuery(self, min_lon, min_lat, max_lon, max_lat):
        query_str = """
            SELECT *
            FROM {table}
            WHERE ST_Intersects(
                wkb_geometry,
                ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
            )
        """
        table_name = "ships"
        query_str = query_str.format(table=table_name)

        return query_str, (min_lon, min_lat, max_lon, max_lat)
=======
            lat=row.get("latitude"),
            lon=row.get("longitude"),
        )


def loadFromCsv(filepath):
    """Charge tous les objets depuis le fichier CSV"""
    items = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = Marker.fromCsvRow(row)
                if item.latitude and item.longitude:
                    items.append(item)
        print(f"✅ {len(items)} items chargés depuis {filepath}")
    except Exception as e:
        print(f"❌ Erreur chargement CSV: {e}")
    return items
>>>>>>> a4a8dd7 (Initial version of the map viewer)


def loadFromDb(db_connector, query, item_class):
    """Charge tous les éléments depuis PostGIS"""
    items = []
    try:
        success, results = db_connector.execute_query(query)
        if success:
            for row in results:
                item = item_class.fromDbRow(row)
<<<<<<< HEAD
                if item.wkb_geometry:
=======
                if item.lat and item.lon:
>>>>>>> a4a8dd7 (Initial version of the map viewer)
                    items.append(item)
        print(f"✅ {len(items)} éléments chargés depuis la base")
    except Exception as e:
        print(f"❌ Erreur chargement DB: {e}")
    return items
