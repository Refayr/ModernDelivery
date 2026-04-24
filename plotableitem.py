import os

from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsSimpleTextItem,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import (
    QBrush,
    QPen,
    QColor,
    QFont,
    QPixmap,
)
from abstractitem import AbstractItem
from osm_graphics_view import OSMGraphicsView


class PlotableItem(AbstractItem):
    """Item that can be plotted over the map"""

    def __init__(
        self,
        id,
        name,
        wkb_geometry,
        img="res/img/marina32.marina32.png",
        size=30.0,
    ):
        super().__init__(id, name, wkb_geometry)
        self.sceneItem = None
        self.img = img
        self.size = size
        self.labelItem = None

        # print(f"SVG Path: {self.svgPath}")
        # print(f"File exists: {os.path.exists(self.svgPath)}")

        # if os.path.exists(self.svgPath):
        #     with open(self.svgPath, "r") as f:
        #         content = f.read()[:200]
        #         print(f"SVG content preview: {content}")

    def plot(self, osmGraphicsView: OSMGraphicsView) -> QGraphicsSvgItem:
        """Draw the marker on the map"""
        # Convertir lat/lon en coordonnées de tuile
        x_tile, y_tile = osmGraphicsView.geometryToTile(
            self.geometry, osmGraphicsView.zoom
        )
        # print(f"🎯 Plotting {self.id} at {x_tile}, {y_tile}")

        x_pix = x_tile * osmGraphicsView.tile_size
        y_pix = y_tile * osmGraphicsView.tile_size
        # print(f"🎯 Plotting {self.id} at {x_pix}, {y_pix}")

        # marker = QGraphicsSvgItem(self.img)
        # if marker.boundingRect().isEmpty() or marker.boundingRect().width() == 0:
        #     print(
        #         f"⚠️ SVG loading error: {self.svgPath} pour {self.name}. Reverting to fallback."
        #     )
        #     # Fallback if invalid SVG
        #     marker = QGraphicsEllipseItem(
        #         x_pix - self.size / 2, y_pix - self.size / 2, 10, 10
        #     )
        #     marker.setBrush(QBrush(self.getColor()))
        #     marker.setPen(QPen(QColor(255, 255, 255), 1))
        # else:
        #     svgRect = marker.boundingRect()
        #     scale = self.size / max(svgRect.width(), svgRect.height())
        #     marker.setScale(scale)

        #     newWidth = svgRect.width() * scale
        #     newHeight = svgRect.height() * scale
        #     marker.setPos(x_pix - newWidth / 2, y_pix - newHeight / 2)
        pixmap = QPixmap(self.img)
        pixmap = pixmap.scaled(
            self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        marker = DataPixmapItem(pixmap, data=self)
        marker.setPos(x_pix - self.size / 2, y_pix - self.size / 2)

        marker.setZValue(1000)
        marker.setToolTip(self.getTooltip())

        return marker

    def plotWithLabel(
        self, osmGraphicsView: OSMGraphicsView
    ) -> (QGraphicsSvgItem, QGraphicsSimpleTextItem):
        """Ajoute un marqueur avec étiquette de nom"""
        marker = self.plot(osmGraphicsView)

        x_tile = marker.pos().x() + marker.boundingRect().width() / 2
        y_tile = marker.pos().y() + marker.boundingRect().height() / 2
        x_pix = x_tile * osmGraphicsView.tile_size
        y_pix = y_tile * osmGraphicsView.tile_size

        label = QGraphicsSimpleTextItem(self.name[:15])  # Tronquer si trop long
        label.setFont(QFont("Arial", 8))
        label.setPos(x_pix + 8, y_pix - 8)
        label.setZValue(11)
        label.setFlag(QGraphicsItem.ItemIsSelectable, False)
        label.userdata = self

        self.labelItem = label
        return marker, label

    def updatePosition(self, osmGraphicsView: OSMGraphicsView):
        """Update location after zooming"""
        if self.sceneItem:
            self.sceneItem = None
            if self.labelItem:
                self.labelItem = None
            self.plotWithLabel(osmGraphicsView)

    def unplot(self, scene: QGraphicsScene):
        """Remove this item from the map"""
        if self.sceneItem and self.sceneItem.scene():
            scene.removeItem(self.sceneItem)
        if self.labelItem and self.labelItem.scene():
            scene.removeItem(self.labelItem)
        self.sceneItem = None
        self.labelItem = None

    def getIconPath(self):
        """Retourne le chemin de l'icône SVG"""
        return self.img

    def getColor(self):
        """Retourne la couleur du marqueur"""
        return QColor(255, 0, 0)  # Rouge

    def getTooltip(self):
        """Retourne le tooltip"""
        return f"{self.name}\nID: {self.id}"


class DataPixmapItem(QGraphicsPixmapItem):
    """QGraphicsPixmapItem avec support de userData"""

    def __init__(self, pixmap, data=None):
        super().__init__(pixmap)
        self._user_data = data

    def setUserData(self, data):
        self._user_data = data

    def userData(self):
        return self._user_data


class DataSvgItem(QGraphicsSvgItem):
    """QGraphicsSvgItem avec support de userData"""

    def __init__(self, file_or_data=None, data=None):
        super().__init__(file_or_data)
        self._user_data = data

    def setUserData(self, data):
        self._user_data = data

    def userData(self):
        return self._user_data
