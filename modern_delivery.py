import sys
from PySide6.QtCore import Signal, QObject, QTimer
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
    data_refreshed = Signal(int)


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

        # Timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.onPeriodicRefresh)
        self.refresh_timer.setInterval(30000)  # 30000 ms = 30s

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
            # self.item_manager.loadSeaportsFromDb(self.db_connector)
            # self.item_manager.loadShipsFromDb(self.db_connector)
            # self.item_manager.loadConnectionsFromDb(self.db_connector)
            success, count = self.item_manager.loadVisibleItemsFromDb(
                self.db_connector, -180.0, -90.0, 180.0, 90.0
            )
            if success:
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

            self.refresh_timer.start()

            if hasattr(self.mainWindow, "mapView") and hasattr(
                self.mainWindow.mapView, "viewChanged"
            ):
                self.mainWindow.mapView.viewChanged.connect(self.onViewChanged)

            self.mainWindow.show()

            if self.mainWindow.statusBar():
                self.mainWindow.statusBar().showMessage(
                    f"✅ Connected to {config['database']}"
                )

        else:
            self.signals.error.emit(msg)
            QMessageBox.critical(None, "Error", msg)
            self.showDbLogin()

    def onViewChanged(self):
        """Appelé quand la vue change (pan, zoom, fin de chargement)"""
        self.refreshTimerSingleShot()

    def refreshTimerSingleShot(self):
        """Débouncing simple : ne recharge que si aucun timer n'est en cours"""
        if hasattr(self, "_pending_refresh"):
            return
        self._pending_refresh = True
        QTimer.singleShot(
            500, self.refreshVisibleData
        )  # Attend 500ms après le dernier mouvement

    def onPeriodicRefresh(self):
        """Appelé toutes les 30 secondes"""
        self.refreshVisibleData()

    def refreshVisibleData(self):
        """
        Recharge uniquement les items visibles dans la vue actuelle.
        """
        if (
            not self.db_connector
            or not self.mainWindow
            or not hasattr(self.mainWindow, "mapView")
        ):
            return

        mapView = self.mainWindow.mapView

        try:
            bbox = mapView.getVisibleBoundingBox()
            if not bbox:
                return
            min_lon, min_lat, max_lon, max_lat = bbox
        except AttributeError:
            bbox = self.calculateViewBbox(mapView)
            if not bbox:
                return
            min_lon, min_lat, max_lon, max_lat = bbox

        success, count = self.item_manager.loadVisibleItemsFromDb(
            self.db_connector, min_lon, min_lat, max_lon, max_lat
        )

        if success:
            self.mainWindow.mapView.renderItems()
            self.signals.data_refreshed.emit(count)
            self.mainWindow.statusBar().showMessage(f"🔄 {count} items refreshed", 2000)
        else:
            self.signals.error.emit("Failed to refresh visible data")

        # Reset du flag de débouncing
        if hasattr(self, "_pending_refresh"):
            delattr(self, "_pending_refresh")

    def calculateViewBbox(self, mapView):
        """
        Calcule manuellement le bounding box si getVisibleBoundingBox n'existe pas.
        Retourne (min_lon, min_lat, max_lon, max_lat) ou None.
        """
        try:
            # Récupérer la rect de la vue visible
            view_rect = mapView.viewport().rect()
            scene_rect = mapView.mapToScene(view_rect).boundingRect()

            # Convertir les coins en coordonnées géographiques
            # On suppose que la scène est en degrés (EPSG:4326)
            p1 = scene_rect.topLeft()
            p2 = scene_rect.bottomRight()

            # Attention : en géographie, Y est la latitude, X est la longitude
            # Mais dans QGraphicsView, Y augmente vers le bas.
            # Si votre scène est en lat/lon standard, topLeft = (min_lon, max_lat)
            # et bottomRight = (max_lon, min_lat)

            min_lon = p1.x()
            max_lon = p2.x()
            max_lat = p1.y()
            min_lat = p2.y()

            return (min_lon, min_lat, max_lon, max_lat)
        except Exception as e:
            print(f"Bbox computation error: {e}")
            return None

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
