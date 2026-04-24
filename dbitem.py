import csv
from abstractitem import AbstractItem


class DBItem(AbstractItem):
    """Item from PostGIS or CSV file"""

    def __init__(self, id, name, wkb_geometry):
        super().__init__(id, name, wkb_geometry)

    @classmethod
    def fromDbRow(cls, row):
        """Create an item from PostGIS"""
        return cls(
            id=row.get("id", ""),
            name=row.get("name", ""),
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


def loadFromDb(db_connector, query, item_class):
    """Charge tous les éléments depuis PostGIS"""
    items = []
    try:
        success, results = db_connector.execute_query(query)
        if success:
            for row in results:
                item = item_class.fromDbRow(row)
                if item.wkb_geometry:
                    items.append(item)
        print(f"✅ {len(items)} éléments chargés depuis la base")
    except Exception as e:
        print(f"❌ Erreur chargement DB: {e}")
    return items
