from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PySide6.QtCore import QFile, QTextStream
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

    def initializeSchemaIfEmpty(self):
        """
        Vérifie si la base contient des tables. Si non, importe les fichiers SQL dans l'ordre.
        Utilise QtSql (QSqlQuery).
        """
        db = self.database
        if not db.isValid() or not db.isOpen():
            return False, "Database not open"

        query = QSqlQuery(db)

        try:
            if not query.exec(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
            ):
                return False, f"Query failed: {query.lastError().text()}"

            if not query.next():
                return False, "Could not read table count"

            table_count = query.value(0)

            if table_count > 0:
                print(f"✅ Database already initialized ({table_count} tables found).")
                return True, "Schema exists"

            print("⚠️ Empty database. Initializing schema...")

            script_files = [
                "res/data/database.1.sql",
                "res/data/database.2.sql",
                "res/data/database.3.sql",
            ]

            base_path = os.getcwd()  # Ou os.path.dirname(__file__) si dans un module

            for i, filename in enumerate(script_files, 1):
                file_path = os.path.join(base_path, filename)

                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"SQL file not found: {file_path}")

                print(f"   Importing file {i}/{len(script_files)} : {filename}...")

                with open(file_path, "r", encoding="utf-8") as f:
                    sql_content = f.read()

                if not query.exec(sql_content):
                    print(f"   ⚠️ Direct execution failed, trying line by line...")
                    commands = sql_content.split(";")
                    for cmd in commands:
                        cmd = cmd.strip()
                        if (
                            cmd
                            and not cmd.startswith("--")
                            and not cmd.startswith("/*")
                        ):
                            if not query.exec(cmd):
                                print(
                                    f"   ⚠️ Error on command: {query.lastError().text()}"
                                )
                                return (
                                    False,
                                    f"Error in {filename}: {query.lastError().text()}",
                                )

                db.commit()

            print("✅ Initialization successfully done.")
            return True, "Schema imported"

        except Exception as e:
            print(f"❌ Error during import: {e}")
            return False, str(e)
