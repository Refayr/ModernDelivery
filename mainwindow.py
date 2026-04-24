from PySide6.QtWidgets import QMainWindow
from osm_graphics_view import OSMGraphicsView
from PySide6.QtCore import QMargins, QObject
from PySide6.QtWidgets import QGridLayout, QToolBar, QStatusBar, QWidget


class MainWindow(QMainWindow):
<<<<<<< HEAD
<<<<<<< HEAD
    def __init__(self, parent=None, item_manager=None):
        super().__init__(parent)
        self.item_manager = item_manager
=======
    def __init__(self, parent=None):
        super().__init__(parent)
>>>>>>> a4a8dd7 (Initial version of the map viewer)
=======
    def __init__(self, parent=None, item_manager=None):
        super().__init__(parent)
        self.item_manager = item_manager
>>>>>>> 8e23b95 (Human readable database.sql)

        self.setWindowTitle("ModernDelivery")

        mapGridLayout = QGridLayout()
        mapGridLayout.setSpacing(0)
        mapGridLayout.setHorizontalSpacing(0)
        mapGridLayout.setVerticalSpacing(0)
        mapGridLayout.setContentsMargins(QMargins(0, 0, 0, 0))

        self.setCentralWidget(QWidget())
        self.createToolBar()

        statusWidget = QStatusBar()
        self.setStatusBar(statusWidget)
        statusWidget.showMessage(
            QObject.tr(
                "Attribution to © OpenStreetMap contributors (https://openstreetmap.org/copyright)"
            )
        )

        self.centralWidget().setLayout(mapGridLayout)
<<<<<<< HEAD
<<<<<<< HEAD
        self.mapView = OSMGraphicsView(
            parent=self, zoom=5, item_manager=item_manager, statusbar=self.statusBar()
        )
=======
        self.mapView = OSMGraphicsView(zoom=5)
>>>>>>> a4a8dd7 (Initial version of the map viewer)
=======
        self.mapView = OSMGraphicsView(zoom=5, item_manager=item_manager)
>>>>>>> 8e23b95 (Human readable database.sql)
        mapGridLayout.addWidget(self.mapView)

    def createToolBar(self):
        toolBar = QToolBar()

        self.addToolBar(toolBar)
