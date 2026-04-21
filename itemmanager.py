from PySide6.QtCore import QObject, Signal
from typing import List, Dict, Type
from abstractitem import AbstractItem
from connection import Connection
from ship import Ship


class ItemManager(QObject):
    items_loaded = Signal(int)
    items_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.items: Dict[str, List[AbstractItem]] = {
            "seaports": [],
            "nodes": [],  # Points de passage futurs
            "ships": [],  # Navires dynamiques
            "connections": [],  # Routes
        }

        # Connexions
        self.connections: List[Connection] = []

        # Types d'éléments
        self.item_types = {
            "seaports": "Seaport",
            "airports": "Airport",
            "vessels": "Vessel",
            "aircrafts": "Aircraft",
        }

        self.visible_types = {
            "seaports": True,
            "nodes": False,  # Cachés par défaut (points de passage)
            "ships": True,
            "connections": True,
        }

    def addItem(self, item_type: str, item: AbstractItem):
        """Ajoute un élément"""
        if item_type in self.items:
            self.items[item_type].append(item)

    def addItems(self, item_type: str, items: List[AbstractItem]):
        """Ajoute plusieurs éléments"""
        if item_type in self.items:
            self.items[item_type].extend(items)
            self.items_loaded.emit(len(items))

    def removeItem(self, item_type: str, item_id: str):
        """Supprime un élément par ID"""
        if item_type in self.items:
            self.items[item_type] = [
                item for item in self.items[item_type] if item.id != item_id
            ]

    def clearItems(self, item_type: str = None):
        """Efface les éléments"""
        if item_type:
            self.items[item_type] = []
        else:
            for key in self.items:
                self.items[key] = []
        self.items_cleared.emit()

    def getItems(self, item_type: str = None) -> List[AbstractItem]:
        """Récupère les éléments"""
        if item_type:
            return self.items.get(item_type, [])
        all_items = []
        for items in self.items.values():
            all_items.extend(items)
        return all_items

    def toggleVisibility(self, item_type: str):
        """Bascule la visibilité d'un type d'élément"""
        if item_type in self.visible_types:
            self.visible_types[item_type] = not self.visible_types[item_type]

    def isVisible(self, item_type: str) -> bool:
        """Vérifie si un type d'élément est visible"""
        return self.visible_types.get(item_type, False)

    def addConnection(self, item1: AbstractItem, item2: AbstractItem):
        """Ajoute une connexion entre deux éléments"""
        connection = Connection(item1, item2)
        self.connections.append(connection)
        return connection

    def clearConnections(self):
        """Efface toutes les connexions"""
        self.connections = []

    def getTotalCount(self) -> int:
        """Retourne le nombre total d'éléments"""
        return sum(len(items) for items in self.items.values())

    def getCountsByType(self) -> Dict[str, int]:
        """Retourne le nombre d'éléments par type"""
        return {key: len(items) for key, items in self.items.items()}

    def loadSeaportsFromDb(self, db_connector):
        """Charge les ports depuis la table Seaports + JOIN"""
        query = """
            SELECT s.id, s.name, n.latitude, n.longitude, c.name as country_name, s.active
            FROM seaports s
            JOIN nodes n ON s.node = n.id
            JOIN countries c ON s.country = c.id
            WHERE s.active = true
        """
        success, results = db_connector.executeQuery(query)
        if success:
            ports = [Seaport.fromDbRow(row) for row in results]
            self.add_items("seaports", ports)
            print(f"✅ {len(ports)} ports chargés")
        return success

    def loadShipsFromDb(self, db_connector):
        """Charge les navires"""
        query = "SELECT * FROM ships WHERE latitude IS NOT NULL"
        success, results = db_connector.executeQuery(query)
        if success:
            ships = [Ship.fromDbRow(row) for row in results]
            self.add_items("ships", ships)
            print(f"✅ {len(ships)} navires chargés")
        return success

    def loadConnectionsFromDb(self, db_connector):
        """Charge les routes entre nodes"""
        query = """
            SELECT n1.id as id1, n2.id as id2,
                   n1.latitude as lat1, n1.longitude as lon1,
                   n2.latitude as lat2, n2.longitude as lon2
            FROM connections c
            JOIN nodes n1 ON c.node1 = n1.id
            JOIN nodes n2 ON c.node2 = n2.id
            WHERE n1.active AND n2.active
        """
        success, results = db_connector.executeQuery(query)
        if success:
            # On crée des objets Connection temporaires pour le dessin
            # Note: Dans une vraie app, on pourrait lier aux objets Node existants
            for row in results:
                # Création d'objets Node temporaires pour tracer la ligne
                n1 = Node(row["id1"], "", row["lat1"], row["lon1"])
                n2 = Node(row["id2"], "", row["lat2"], row["lon2"])
                conn = Connection(n1, n2)
                self.connections.append(conn)
            print(f"✅ {len(results)} connections loaded")
        return success
