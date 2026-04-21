from PySide6.QtWidgets import QMainWindow
from osm_graphics_view import OSMGraphicsView
from PySide6.QtCore import QMargins, QObject
from PySide6.QtWidgets import QGridLayout, QToolBar, QStatusBar, QWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.mapView = OSMGraphicsView(zoom=5)
        mapGridLayout.addWidget(self.mapView)

    def createToolBar(self):
        toolBar = QToolBar()

        self.addToolBar(toolBar)
