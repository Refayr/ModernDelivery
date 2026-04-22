import sys
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtCore import QMargins

from mainwindow import MainWindow
from db_credentials import CredentialStorage
from db_connector import PostGISConnector
from db_login_widget import DBLoginDialog
from itemmanager import ItemManager


class ModernDeliverySignals(QObject):
    """Signaux globaux pour l'application"""

    db_connected = Signal()
    db_disconnected = Signal()
    ports_loaded = Signal(int)
    error = Signal(str)


class ModernDelivery(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName("ModernDelivery")
        self.setApplicationVersion("1.0")
        self.setOrganizationName("Polytechnique")

        # Gestionnaire de base de données
        self.db_connector: PostGISConnector = None
        self.item_manager = ItemManager(self)
        self.signals = ModernDeliverySignals()

        # Vérifier les credentials sauvegardés
        self.credentials_storage = CredentialStorage()

        self.mainWindow = None

        # Initialiser
        self.initialize()

    def initialize(self):
        """Initialisation de l'application"""
        if self.credentials_storage.hasCredentials():
            # Charger et connecter automatiquement
            success, creds = self.credentials_storage.loadCredentials()
            if success:
                self.connectToDb(creds)
            else:
                self.showDbLogin()
        else:
            self.showDbLogin()

    def initializeData(self):
        """Charge toutes les données depuis PostGIS"""
        if not self.db_connector or not self.mainWindow:
            return

        try:
            self.item_manager.loadSeaportsFromDb(self.db_connector)
            self.item_manager.loadShipsFromDb(self.db_connector)
            self.item_manager.loadConnectionsFromDb(self.db_connector)
            self.mainWindow.mapView.renderItems()

            counts = self.item_manager.getCountsByType()
            total = sum(counts.values())

            message = f"✅ {total} items loaded ({counts['seaports']} seaports, {counts['ships']} ships)"
            self.mainWindow.statusBar().showMessage(message)

        except Exception as e:
            self.signals.error.emit(f"Error loading data: {str(e)}")
            QMessageBox.critical(self.mainWindow, "Error", str(e))

    def showDbLogin(self):
        """Affiche le widget de connexion"""
        dialog = DBLoginDialog()
        if dialog.exec() == QDialog.Accepted:
            creds = dialog.getCredentials()
            self.connectToDb(creds)
        else:
            # Annulation - quitter ou attendre
            self.signals.error.emit("Connection aborted")
            sys.exit(0)

    def connectToDb(self, config):
        """Connecte à la base de données"""
        self.db_connector = PostGISConnector(config)
        success, msg = self.db_connector.connect()

        if success:
            self.signals.db_connected.emit()

            if not self.mainWindow:
                self.createMainWindow()

            self.initializeData()

            self.mainWindow.show()

            if self.mainWindow.statusBar():
                self.mainWindow.statusBar().showMessage(
                    f"✅ Connected to {config['database']}"
                )

        else:
            self.signals.error.emit(msg)
            QMessageBox.critical(None, "Error", msg)
            self.showDbLogin()

    def disconnectDb(self):
        """Déconnecte de la base"""
        if self.db_connector:
            self.db_connector.disconnect()
            self.db_connector = None
            self.signals.db_disconnected.emit()

    def createMainWindow(self):
        """Crée la fenêtre principale"""

        self.mainWindow = MainWindow(None, self.item_manager)
        self.mainWindow.setWindowTitle("MapView - ModernDelivery")

    def getDbConnector(self):
        """Retourne le connecteur de base de données"""
        return self.db_connector

    def quitApplication(self):
        """Quitte proprement l'application"""
        self.disconnectDb()
        self.quit()

    def showWindow(self):
        if self.mainWindow:
            self.mainWindow.show()
