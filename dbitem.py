import csv
from abstractitem import AbstractItem


class DBItem(AbstractItem):
    """Item from PostGIS or CSV file"""

    def __init__(self, id, name, lat, lon):
        super().__init__(id, name, lat, lon)

    @classmethod
    def fromDbRow(cls, row):
        """Create an item from PostGIS"""
        return cls(
            id=row.get("id", ""),
            name=row.get("name", ""),
            lat=row.get("latitude"),
            lon=row.get("longitude"),
        )


def loadFromDb(db_connector, query, item_class):
    """Charge tous les éléments depuis PostGIS"""
    items = []
    try:
        success, results = db_connector.execute_query(query)
        if success:
            for row in results:
                item = item_class.fromDbRow(row)
                if item.lat and item.lon:
                    items.append(item)
        print(f"✅ {len(items)} éléments chargés depuis la base")
    except Exception as e:
        print(f"❌ Erreur chargement DB: {e}")
    return items
