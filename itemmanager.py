from PySide6.QtCore import QObject, Signal

from typing import List, Dict, Type
from abstractitem import AbstractItem
from ship import Ship
from seaport import Seaport


class ItemManager(QObject):
    items_loaded = Signal(int)
    items_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.items: Dict[str, List[AbstractItem]] = {
            "seaports": [],
            "ships": [],
        }

        # Types d'éléments
        self.item_types = {
            "seaports": "Seaport",
            # "airports": "Airport",
            "ships": "Ship",
            # "aircrafts": "Aircraft",
        }

        self.visible_types = {
            "seaports": True,
            "ships": True,
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

    def getTotalCount(self) -> int:
        """Retourne le nombre total d'éléments"""
        return sum(len(items) for items in self.items.values())

    def getCountsByType(self) -> Dict[str, int]:
        """Retourne le nombre d'éléments par type"""
        return {key: len(items) for key, items in self.items.items()}

    def loadVisibleItemsFromDb(self, db_connector, min_lon, min_lat, max_lon, max_lat):
        """Charge les Ships et Seaports dans la zone visible. Remplace les données existantes uniquement pour ces types dans cette zone."""
        if not db_connector.isConnected():
            return False, 0

        total_loaded = 0

        print(min_lon, max_lon, min_lat, max_lat)

        # Ships
        success, new_items = Ship.loadVisibleItemsFromDb(
            db_connector, min_lon, min_lat, max_lon, max_lat
        )
        if success:
            self.items["ships"] = new_items
            total_loaded += len(new_items)
            print(f"Ships: {len(new_items)} loaded")

        # Seaports
        success, new_items = Seaport.loadVisibleItemsFromDb(
            db_connector, min_lon, min_lat, max_lon, max_lat
        )
        if success:
            self.items["seaport"] = new_items
            total_loaded += len(new_items)
            print(f"Seaports: {len(new_items)} loaded")

        return True, total_loaded

    def clearAllItems(self):
        """Optionnel : Pour réinitialiser tout si on veut recharger TOUT la base (cas démarrage)"""
        for key in self.items:
            self.items[key] = []
