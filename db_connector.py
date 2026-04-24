from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from typing import Optional, List, Dict, Tuple


class PostGISConnector:
    """Connection manager for PostGIS using QtSQL"""

    CONNECTION_NAME = "PostGIS_Main"

    def __init__(self, config: dict):
        self.config = config
        self.database: Optional[QSqlDatabase] = None

    def connect(self) -> Tuple[bool, str]:
        """Connects to PostGIS"""
        drivers = QSqlDatabase.drivers()
        if "QPSQL" not in drivers:
            return (
                False,
                "PostgreSQL driver (QPSQL) unavailable. Install Qt with PostgreSQL support.",
            )

        self.database = QSqlDatabase.addDatabase("QPSQL", self.CONNECTION_NAME)
        self.database.setHostName(self.config["host"])
        self.database.setPort(self.config["port"])
        self.database.setDatabaseName(self.config["database"])
        self.database.setUserName(self.config["username"])
        self.database.setPassword(self.config["password"])

        if not self.database.open():
            error = self.database.lastError().text()
            QSqlDatabase.removeDatabase(self.CONNECTION_NAME)
            return False, f"Connection failed: {error}"

        query = QSqlQuery(self.database)
        if not query.exec("SELECT postgis_version()"):
            error = query.lastError().text()
            self.disconnect()
            return (
                False,
                f"PostGIS not dectected: {error}\nConsider typing the following command in psql> CREATE EXTENSION postgis;",
            )

        return True, "Connected to PostGIS"

    def disconnect(self):
        """Closes connection"""
        if self.database and self.database.isOpen():
            self.database.close()
            QSqlDatabase.removeDatabase(self.CONNECTION_NAME)
            self.database = None

    def isConnected(self) -> bool:
        """Check if the connection is active"""
        return self.database is not None and self.database.isOpen()

    def executeQuery(
        self, query_str: str, values: tuple = ()
    ) -> Tuple[bool, List[Dict]]:
        """Executes a query and returns results"""
        if not self.isConnected():
            return False, []

        query = QSqlQuery(self.database)

        if values:
            if not query.prepare(query_str):
                return False, [query.lastError().text()]

            for value in values:
                query.addBindValue(value)

            if not query.exec():
                return False, [query.lastError().text()]
        else:
            if not query.exec(query_str):
                return False, [query.lastError().text()]

        results = []
        while query.next():
            record = query.record()
            row = {}
            for i in range(record.count()):
                field_name = record.fieldName(i)
                row[field_name] = record.value(i)
            results.append(row)

        return True, results

    def getSeaports(self, country: str = None, limit: int = 100) -> List[Dict]:
        """Get seaports from PostGIS"""
<<<<<<< HEAD
        print("SERT A RIEN - TO DELETE")
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        query = """
            SELECT
                name,
                country,
                port_id,
<<<<<<< HEAD
                ST_Y(wkb_geometry) as latitude,
                ST_X(wkb_geometry) as longitude,
=======
                ST_Y(geom) as latitude,
                ST_X(geom) as longitude,
                url
>>>>>>> a4a8dd7 (Initial version of the map viewer)
            FROM ports
        """
        params = []

        if country:
            query += " WHERE country = %s"
            params.append(country)

        query += f" LIMIT {limit}"

        success, results = self.executeQuery(query, tuple(params))
        if success:
            return results
        return []

    def getAllCountries(self) -> List[str]:
        """Récupère la liste des pays uniques"""
<<<<<<< HEAD
        print("SERT A RIEN - TO DELETE")
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        success, results = self.executeQuery(
            "SELECT DISTINCT country FROM ports ORDER BY country"
        )
        if success:
            return [row["country"] for row in results]
        return []

    def getSeaportCount(self) -> int:
        """Gets total number of seaports"""
<<<<<<< HEAD
        print("SERT A RIEN - TO DELETE")
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        success, results = self.executeQuery("SELECT COUNT(*) as count FROM Seaports")
        if success and results:
            return results[0]["count"]
        return 0
