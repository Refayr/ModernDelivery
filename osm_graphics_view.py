import re
import math

<<<<<<< HEAD

from functools import partial
from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QRectF
=======
from searchwidget import SearchWidget

from functools import partial
from PySide6.QtCore import QUrl, QTimer
>>>>>>> a4a8dd7 (Initial version of the map viewer)
from PySide6.QtGui import QPixmap, QPainter, QBrush, QPen, QColor, QFont
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QPushButton,
    QLabel,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
)
from PySide6.QtSvgWidgets import QGraphicsSvgItem

<<<<<<< HEAD
from shapely import wkb

from searchwidget import SearchWidget
from network_access_manager import NetworkAccessManager
from abstractitem import AbstractItem
=======
from network_access_manager import NetworkAccessManager

# from plotableitem import PlotableItem
<<<<<<< HEAD
from itemmanager import ItemManager
>>>>>>> a4a8dd7 (Initial version of the map viewer)
=======
# from itemmanager import ItemManager
>>>>>>> 8e23b95 (Human readable database.sql)


def check_and_extract_numbers(filename):
    # Template for file name validation
    pattern = r"^(\d+)_(\d+)_(\d+)\_tile$"

    # Checking if the file name matches the pattern
    match = re.match(pattern, filename)

    if match:
<<<<<<< HEAD
        numbers = match.groups()
        return True, [int(v) for v in numbers]
    return False, []


class OSMGraphicsView(QGraphicsView):
    viewChanged = Signal()

    def __init__(self, zoom=2, parent=None, item_manager=None, statusbar=None):
        super().__init__(parent)

        self._initialized = False

=======
        # If it matches, we extract the numbers
        numbers = match.groups()
        return True, [int(v) for v in numbers]
    else:
        # If it doesn't match, return False and an empty list.
        return False, list()


class OSMGraphicsView(QGraphicsView):
    def __init__(self, zoom=2, parent=None, item_manager=None):
        super().__init__(parent)

>>>>>>> a4a8dd7 (Initial version of the map viewer)
        # Render settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheNone)

        self.tile_size = 256  # One-interval size in pixels
        self.zoom = zoom  # Current level of the zoom
        self.tiles = {}  # Loaded tabs: key (zoom, x, y, world_offset)
        self._fade_anim_group = None  # Animation group link fade-out

<<<<<<< HEAD
        self.statusbar = statusbar
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.updateSceneRect()

        # Assumes NetworkAccessManagerPool is defined
        self.network_manager = NetworkAccessManager(self, max_concurrent=5)
        self.network_manager.tile_loaded.connect(self._onTileLoaded)
        self.tile_cache = {}
<<<<<<< HEAD
        self._last_view_bbox = None
        self._move_threshold = 50  # Minimum 50 pixels de déplacement avant refresh
        self._last_mouse_pos = None
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)

        self.setupAttribution()

        # Initial batch load
        self.updateTiles()

        self.h_margin = 20
        self.w_margin = 20

        self.findLine = SearchWidget(self)
        self.findLine.move(self.w_margin, self.h_margin)
        self.findLine.changedLocation.connect(self.fitToBoundingBox)

        self.plusButton = QPushButton("+", self)
        self.plusButton.setFixedSize(30, 30)
        self.plusButton.move(self.width() - self.w_margin, self.h_margin)
        self.plusButton.clicked.connect(self.upZoomEvent)

        self.minusButton = QPushButton("-", self)
        self.minusButton.setFixedSize(30, 30)
        self.minusButton.move(self.width() - self.w_margin, self.h_margin)
        self.minusButton.clicked.connect(self.downZoomEvent)

        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._delayedUpdateTiles)

        self.seaportMarkers = []
        self.seaportLabels = []
<<<<<<< HEAD
<<<<<<< HEAD

        self.item_manager = item_manager
=======
        # self.loadSeaports("res/csv/seaports.csv")

        self.item_manager = ItemManager(self)
>>>>>>> a4a8dd7 (Initial version of the map viewer)
=======

        self.item_manager = item_manager
>>>>>>> 8e23b95 (Human readable database.sql)
        self.item_manager.items_loaded.connect(self.onItemsLoaded)
        self.item_manager.items_cleared.connect(self.onItemsCleared)

        self.scene_items = []
        self.scene_labels = []
<<<<<<< HEAD

    def showEvent(self, event):
        super().showEvent(event)
        # print("🖥️ showEvent déclenché")  # DEBUG

        if not self._initialized:
            # Center on straight of Ormuz
            # self.centerOnTile(42, 27, 6)
            self._initialized = True

        self.viewChanged.emit()
=======
        self.scene_connections = []
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    def onItemsLoaded(self, count):
        """Quand des éléments sont chargés"""
        self.renderItems()
<<<<<<< HEAD
        if self.statusbar:
            self.statusbar.showMessage(f"✅ {count} éléments chargés")
=======
        self.statusBar().showMessage(f"✅ {count} éléments chargés")
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    def onItemsCleared(self):
        """Quand les éléments sont effacés"""
        self.clearSceneItems()

    def renderItems(self):
        """Affiche tous les éléments visibles"""
        self.clearSceneItems()

        for item_type, items in self.item_manager.items.items():
            if not self.item_manager.isVisible(item_type):
                continue

            for item in items:
                try:
<<<<<<< HEAD
                    if hasattr(item, "plot"):
                        # marker, label = item.plotWithLabel(self)
                        marker = item.plot(self)
                        self.scene.addItem(marker)
                        # self.scene.addItem(label)
                        self.scene_items.append(marker)
                        # self.scene_labels.append(label)
                except Exception as e:
                    print(f"❌ draw error {item.name}: {e}")

=======
                    if hasattr(item, "plotWithLabel"):
                        marker, label = item.plotWithLabel(self)
                        self.scene.addItem(marker)
                        self.scene.addItem(label)
                        self.scene_items.append(marker)
                        self.scene_labels.append(label)
                except Exception as e:
                    print(f"❌ draw error {item.name}: {e}")

        # Dessiner les connexions
        self.renderConnections()

    def renderConnections(self):
        """Affiche toutes les connexions"""
        for connection in self.item_manager.connections:
            line = connection.draw(self)
            self.scene.addItem(line)
            self.scene_connections.append(line)

>>>>>>> a4a8dd7 (Initial version of the map viewer)
    def clearSceneItems(self):
        """Nettoie tous les éléments graphiques"""
        for item in self.scene_items:
            if item.scene():
                self.scene.removeItem(item)
        for label in self.scene_labels:
            if label.scene():
                self.scene.removeItem(label)
<<<<<<< HEAD

        self.scene_items.clear()
        self.scene_labels.clear()

    def updateMarkers(self):
=======
        for conn in self.scene_connections:
            if conn.scene():
                self.scene.removeItem(conn)

        self.scene_items.clear()
        self.scene_labels.clear()
        self.scene_connections.clear()

    # def loadSeaports(self, filepath):
    #     """Charge et affiche les ports sur la carte"""
    #     seaports = loadFromCsv(filepath)

    #     for port in seaports:
    #         self.addMarker(port)
    #         # self.addMarkerWithLabel(port)

    #     print(f"📍 {len(ports)} ports affichés sur la carte")

    # def addMarker(self, marker: PlotableItem()):
    #     """Ajoute un marqueur à la carte"""
    #     mark = marker.plot(self)

    #     self.scene.addItem(mark)
    #     self.seaportMarkers.append(mark)

    # def addMarkerWithLabel(self, marker: PlotableItem()):
    #     """Ajoute un marqueur avec étiquette de nom"""
    #     mark, label = marker.plot(self)

    #     self.scene.addItem(mark)
    #     self.scene.addItem(label)
    #     self.seaportMarkers.append(mark)
    #     self.seaportLabels.append(label)

    def updatePortMarkers(self):
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        """Recalcule la position des marqueurs après changement de zoom"""
        self.renderItems()

    def fitToBoundingBox(self, south, north, west, east):
        """
        Customizes the map’s visibility area to cover `boundingbox`.

        boundingbox = [south, north, west, east] (latitude and longitude in degrees).
        """

        print(south, north, west, east)

        # Check that the coordinates are correct
        if south >= north or west >= east:
            print("Error: Incorrect boundaries boundingbox")
            return

        # Find the center of boundingbox
        center_lat = (south + north) / 2.0
        center_lon = (west + east) / 2.0

        # Find the level of a zoom that will put the entire area on screen
        self.zoom = self.calculateBestZoom(south, north, west, east)
        self.updateSceneRect()

        # Convert center to pixel coordinates
        x_tile, y_tile = self.latLonToTile(center_lat, center_lon, self.zoom)
        x_pix = x_tile * self.tile_size
        y_pix = y_tile * self.tile_size

        # Set new map center
        self.centerOn(x_pix, y_pix)
        self.updateTiles()

        print(
            f"Map moved to BBOX: lat={center_lat}, lon={center_lon}, zoom={self.zoom}"
        )

<<<<<<< HEAD
    def getVisibleBoundingBox(self):
        """
        Retourne (min_lon, min_lat, max_lon, max_lat) de la zone visible.
        """
        scene = self.scene
        if not scene:
            print("❌ getVisibleBoundingBox: No scene")
            return None

        scene_rect = scene.sceneRect()
        if scene_rect.isEmpty():
            print("❌ getVisibleBoundingBox: SceneRect is empty (0,0,0,0)")
            # return (-180, -90, 180, 90)   # World
            return None

        view_rect = self.viewport().rect()
        if view_rect.width() <= 0 or view_rect.height() <= 0:
            print("❌ getVisibleBoundingBox: Viewport size is 0")
            return None

        scene_view_rect = self.mapToScene(view_rect).boundingRect()

        if scene_view_rect.isEmpty():
            print("❌ getVisibleBoundingBox: MapToScene returns nothing")
            return None

        min_tile_x = scene_view_rect.left() / self.tile_size
        min_tile_y = scene_view_rect.top() / self.tile_size
        max_tile_x = scene_view_rect.right() / self.tile_size
        max_tile_y = scene_view_rect.bottom() / self.tile_size

        max_lat, min_lon = self.tileToLatLon(min_tile_x, min_tile_y, self.zoom)
        min_lat, max_lon = self.tileToLatLon(max_tile_x, max_tile_y, self.zoom)
        if min_lon >= max_lon or min_lat >= max_lat:
            print(
                f"❌ Invalid BBox: min({min_lat}, {min_lon}) >= max({max_lat}, {max_lon})"
            )
            return None

        # Debug
        # print(f"Pixels: {scene_view_rect.left():.0f}, {scene_view_rect.top():.0f}")
        # print(f"Tuiles: [{min_tile_x:.2f}, {min_tile_y:.2f}] -> [{max_tile_x:.2f}, {max_tile_y:.2f}]")
        # print(f"Degrés: Lon[{min_lon:.2f}, {max_lon:.2f}], Lat[{min_lat:.2f}, {max_lat:.2f}]")

        return (min_lon, min_lat, max_lon, max_lat)

    @staticmethod
    def tileToLatLon(x_tile, y_tile, zoom):
        """Convertit une coordonnée de tuile en lat/lon"""
        n = 2**zoom
        lon = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat = math.degrees(lat_rad)
        return lat, lon

=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
    def calculateBestZoom(self, south, north, west, east):
        """
        Calculates the optimal level of a zoom so that the boundingbox is fully embedded in the window.
        """
        for z in range(19, 0, -1):  # We’re going from 19 to 0
            x_min, y_max = self.latLonToTile(north, west, z)
            x_max, y_min = self.latLonToTile(south, east, z)

            # Size of the boundingbox in pixels
            width_px = (x_max - x_min) * self.tile_size
            height_px = (y_max - y_min) * self.tile_size

            # Check if it’s going into the window
            if (
                width_px <= self.viewport().width()
                and height_px <= self.viewport().height()
            ):
                return z  # Return the first suitable zoom

        return None  # If nothing is found, leave the current one

<<<<<<< HEAD
    def geometryToTile(self, wkb_geometry, zoom):
        if isinstance(wkb_geometry, bytes):
            try:
                wkb_geometry = wkb.loads(wkb_geometry)
            except Exception as e:
                raise ValueError(f"Impossible to parse WKB: {e}")

        if wkb_geometry is None:
            raise ValueError("Geometry must not be None")

        if hasattr(wkb_geometry, "x") and hasattr(wkb_geometry, "y"):
            lon = wkb_geometry.x
            lat = wkb_geometry.y
        elif hasattr(wkb_geometry, "coords"):
            # Polygon, LineString
            coords = list(wkb_geometry.coords)
            if len(coords) == 0:
                raise ValueError("No coordinates in this geometry")
            lon, lat = coords[0]
        else:
            raise ValueError(f"Unsupported geometry: {type(wkb_geometry)}")

        return self.latLonToTile(lat, lon, zoom)

=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
    def latLonToTile(self, lat, lon, zoom):
        """
        Converts latitude and longitude to a secret coordinate (x, y) for the given zoom.
        """
        n = 2**zoom
        x_tile = (lon + 180.0) / 360.0 * n
        y_tile = (
            (
                1.0
                - math.log(
                    math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))
                )
                / math.pi
            )
            / 2.0
            * n
        )
        return x_tile, y_tile

    def moveToCoordinates(self, lat, lon):
        """
        Moves the map view to specified coordinates (lat, lon).
        """
        # Check that the zoom is set correctly
        if not (0 <= self.zoom <= 19):
            print("Error: Incorrect zoom level")
            return

        # Convert latitude and longitude to subtle coordinates
        n = 2**self.zoom  # Number of rows in the row at this level in a zoom
        x_tile = (lon + 180.0) / 360.0 * n
        y_tile = (
            (
                1.0
                - math.log(
                    math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))
                )
                / math.pi
            )
            / 2.0
            * n
        )

        # Convert the secret coordinates to pixels
        x_pix = x_tile * self.tile_size
        y_pix = y_tile * self.tile_size

        # Move map center to computed coordinates
        self.centerOn(x_pix, y_pix)
        self.updateTiles()

        print(f"Moved to coordinates: lat={lat}, lon={lon}, x={x_pix}, y={y_pix}")

    def updateSceneRect(self):
        """
        Resize the scene with horizontal repetition.
        Set the stage width to 3 times the base card width,
        To repeat the map border when scrolling across the left or right.
        """

        world_width = self.tile_size * (2**self.zoom)
        self.scene.setSceneRect(0, 0, world_width + 0.1 * world_width, world_width)

    def updateTiles(self):
        """
        Determine which time zones should be displayed with horizontal rotation.
        Calculate the area of the visible part of the scene and for each coordinate x, y
<<<<<<< HEAD
        calculate the rounded coordinates with x % n_tiles and world_offset = x - (x % n_tiles).
=======
        calculate the rounded coordinates with x % n_tiles и world_offset = x - (x % n_tiles).
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        """
        rect = self.mapToScene(self.viewport().rect()).boundingRect()
        x_min = int(rect.left() // self.tile_size)
        x_max = int(rect.right() // self.tile_size) + 1
        y_min = int(rect.top() // self.tile_size)
        y_max = int(rect.bottom() // self.tile_size) + 1
        n_tiles = 2**self.zoom
<<<<<<< HEAD
        # print(f"Viewport: x[{x_min}, {x_max}] y[{y_min}, {y_max}] zoom{self.zoom}")
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)

        for x in range(x_min, x_max + 1):
            wrapped_x = x % n_tiles
            world_offset = x - wrapped_x
            for y in range(y_min, y_max + 1):
                if y < 0 or y >= n_tiles:
                    continue  # No vertical roll-up required
                key = (self.zoom, wrapped_x, y, world_offset)
                if key not in self.tiles:
                    # self.preLoadTile(wrapped_x, y, self.zoom, world_offset)
                    self.loadTile(wrapped_x, y, self.zoom, world_offset)

    def loadTile(self, x, y, z, world_offset=0):
        """
        Generate URL and run asynchronous time loading with offset.
        """
        key = (z, x, y)

        if key in self.tile_cache:
            self._addTileToScene(x, y, z, world_offset, self.tile_cache[key])
            return

        url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        self.network_manager.requestTile(url)
<<<<<<< HEAD
        self.viewChanged.emit()
=======

        # request = QNetworkRequest(QUrl(url))
        # reply = self.network_manager_pool.getNetworkManager().get(request)
        # reply.finished.connect(
        #     partial(self.handleTileReply, reply, x, y, z, world_offset)
        # )
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    def handleTileReply(self, reply, x, y, z, world_offset):
        """
        Process the response and add the time to the stage.
        If the zoom level has already changed, the response is ignored.
        """
        if z != self.zoom:
            reply.deleteLater()
            return

        err = reply.error()
        if err != QNetworkReply.NetworkError.NoError:
            print(f"Error: {err} Time loading error {z}/{x}/{y}: {reply.errorString()}")
            reply.deleteLater()
            return

        data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if pixmap.isNull():
            print(f"I can’t load the timeline ({z}/{x}/{y})")
            reply.deleteLater()
            return

        item = QGraphicsPixmapItem(pixmap)
        # Positioning with horizontal reversal:
        # (x + world_offset) takes into account the map’s left and right-hand repetitions.
        item.setPos((x + world_offset) * self.tile_size, y * self.tile_size)
        item.setZValue(1)
        self.scene.addItem(item)
        self.tiles[(z, x, y, world_offset)] = item

        reply.deleteLater()

    def wheelEvent(self, event):
        """
        When changing a zoom:
          - Old secrets are preserved for smooth fade-out.
          - Calculate a new level of the zoom, update the stage dimensions and center.
          - After loading new trays for a new tooth, the old ones disappear smoothly.
        """
<<<<<<< HEAD
        super().wheelEvent(event)
        # print("🔍 wheelEvent déclenché")  # DEBUG
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)

        visibleRect = self.mapToScene(self.viewport().rect()).boundingRect()
        sceneRect = self.scene.sceneRect()

        if visibleRect.width() >= sceneRect.width():
            self.scene.clear()
            self.scene.setSceneRect(visibleRect)

        delta = event.angleDelta().y()
        old_zoom = self.zoom
        if delta > 0:
            new_zoom = min(self.zoom + 1, 19)
        else:
            new_zoom = max(self.zoom - 1, 0)
        if new_zoom == old_zoom:
            return

        # Keep old secrets and clean the dictionary for new ones
        old_items = list(self.tiles.values())
        self.tiles.clear()

        # Calculate new center position
        cursor_scene_pos = self.mapToScene(event.position().toPoint())
        factor = pow(2, new_zoom - old_zoom)
        new_center = cursor_scene_pos * factor

        self.zoom = new_zoom
        self.updateSceneRect()
        self.centerOn(new_center)
        self.updateTiles()

<<<<<<< HEAD
        self.updateMarkers()

        print(f"ZOOM: {self.zoom}")
        self.viewChanged.emit()
=======
        self.updatePortMarkers()

        print(f"ZOOM: {self.zoom}")
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    def cleanupOldTiles(self, items):
        for item in items:
            self.scene.removeItem(item)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.plusButton.move(
            self.width() - self.w_margin - self.plusButton.width(), self.h_margin
        )
        self.minusButton.move(
            self.width() - self.w_margin - self.plusButton.width(), 2.5 * self.h_margin
        )

        if hasattr(self, "attribution_label"):
            self.attribution_label.move(
                self.width() - self.attribution_label.width() - 10,
                self.height() - self.attribution_label.height() - 10,
            )

        self.updateTiles()

    def upZoomEvent(self):
        new_zoom = self.zoom + 1
        old_zoom = self.zoom

        if new_zoom > 19 or new_zoom < 0:
            return

        visibleRect = self.mapToScene(self.viewport().rect()).boundingRect()
        sceneRect = self.scene.sceneRect()

        if visibleRect.width() >= sceneRect.width():
            self.scene.clear()
            self.scene.setSceneRect(visibleRect)

        self.tiles.clear()

        # Calculate new center position
        cursor_scene_pos = visibleRect.center().toPoint()
        factor = pow(2, new_zoom - old_zoom)
        new_center = cursor_scene_pos * factor

        self.zoom = new_zoom
        self.updateSceneRect()
        self.centerOn(new_center)
        self.updateTiles()

<<<<<<< HEAD
        self.updateMarkers()
=======
        self.updatePortMarkers()
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    def downZoomEvent(self):
        new_zoom = self.zoom - 1
        old_zoom = self.zoom

        if new_zoom > 19 or new_zoom < 0:
            return

        visibleRect = self.mapToScene(self.viewport().rect()).boundingRect()
        sceneRect = self.scene.sceneRect()

        if visibleRect.width() >= sceneRect.width():
            self.scene.clear()
            self.scene.setSceneRect(visibleRect)

        self.tiles.clear()

        # Calculate new center position
        cursor_scene_pos = visibleRect.center().toPoint()
        factor = pow(2, new_zoom - old_zoom)
        new_center = cursor_scene_pos * factor

        self.zoom = new_zoom
        self.updateSceneRect()
        self.centerOn(new_center)
        self.updateTiles()

<<<<<<< HEAD
        self.updateMarkers()

    def centerOnTile(self, x_tile, y_tile, zoom):
        # TODO Ne fonctionne pas correctement
        """
        Centre la vue sur une tuile spécifique.
        """
        n = 2**zoom
        min_lon = x_tile / n * 360.0 - 180.0
        max_lon = (x_tile + 1) / n * 360.0 - 180.0

        min_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y_tile + 1) / n)))
        max_lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        min_lat = math.degrees(min_lat_rad)
        max_lat = math.degrees(max_lat_rad)

        padding = 0.1
        scene_rect = QRectF(
            min_lon - padding,
            min_lat - padding,
            (max_lon - min_lon) + 2 * padding,
            (max_lat - min_lat) + 2 * padding,
        )

        self.scene.setSceneRect(scene_rect)

        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        self.centerOn(center_lon, center_lat)

        tile_rect = QRectF(min_lon, min_lat, max_lon - min_lon, max_lat - min_lat)
        self.fitInView(tile_rect, Qt.AspectRatioMode.KeepAspectRatio)
=======
        self.updatePortMarkers()
>>>>>>> a4a8dd7 (Initial version of the map viewer)

    def isNearMapBoundary(self, margin=50):
        # We get a visible area in the scene coordinates
        visibleRect = self.mapToScene(self.viewport().rect()).boundingRect()
        # We get scene boundaries
        sceneRect = self.scene.sceneRect()

        nearLeft = visibleRect.left() <= sceneRect.left() + margin
        nearRight = visibleRect.right() >= sceneRect.right() - margin
        nearTop = visibleRect.top() <= sceneRect.top() + margin
        nearBottom = visibleRect.bottom() >= sceneRect.bottom() - margin

        return nearLeft, nearRight, nearTop, nearBottom

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
<<<<<<< HEAD
        # print("📍 mouseMoveEvent déclenché")  # DEBUG

        current_pos = event.position().toPoint()

        if self._last_mouse_pos:
            distance = (current_pos - self._last_mouse_pos).manhattanLength()

            if distance < self._move_threshold:
                return

        self._last_mouse_pos = current_pos
=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)

        # Arrêter le timer précédent
        self.update_timer.stop()

        # Redémarrer avec délai de 200ms
        self.update_timer.start(200)

<<<<<<< HEAD
        self.viewChanged.emit()

=======
>>>>>>> a4a8dd7 (Initial version of the map viewer)
    def _delayedUpdateTiles(self):
        """Méthode appelée après le debounce"""
        self.updateTiles()

    def mousePressEvent(self, event):
        """✅ Clic sur un port affiche les détails"""
        item = self.itemAt(event.position().toPoint())

        if item and hasattr(item, "userData"):
            geo_item = item.userData
            if isinstance(geo_item, AbstractItem):
                print(f"📍 Selection: {geo_item.name}")
                if hasattr(self.parent(), "statusBar"):
                    self.parent().statusBar().showMessage(geo_item.get_tooltip())

            # ✅ Afficher dans la statusBar
            # if hasattr(self.parent(), "statusBar"):
            #     self.parent().statusBar().showMessage(
            #         f"{port.name}, {port.country} (ID: {port.port_id})"
            #     )

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.updateTiles()

    def _onTileLoaded(self, url, data):
        """
        Traitement de la tuile reçue + mise en cache
        """
        pixmap = QPixmap()
        pixmap.loadFromData(data)

        if pixmap.isNull():
            return

        # Extraire z, x, y de l'URL pour le cache
        match = re.search(r"/(\d+)/(\d+)/(\d+)\.png$", url)
        if match:
            z, x, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
            key = (z, x, y)
            self.tile_cache[key] = pixmap

            # Limiter la taille du cache (ex: 100 tuiles max)
            if len(self.tile_cache) > 100:
                oldest_key = next(iter(self.tile_cache))
                del self.tile_cache[oldest_key]

        rect = self.mapToScene(self.viewport().rect()).boundingRect()
        x_min = int(rect.left() // self.tile_size)
        x_max = int(rect.right() // self.tile_size) + 1
        y_min = int(rect.top() // self.tile_size)
        y_max = int(rect.bottom() // self.tile_size) + 1

        if x_min <= x <= x_max and y_min <= y <= y_max:
            # Trouver le world_offset approprié
            n_tiles = 2**self.zoom
            wrapped_x = x % n_tiles
            world_offset = x - wrapped_x
            self._addTileToScene(wrapped_x, y, z, world_offset, pixmap)

    def _addTileToScene(self, x, y, z, world_offset, pixmap):
        """Ajoute une tuile à la scène"""
        item = QGraphicsPixmapItem(pixmap)
        item.setPos((x + world_offset) * self.tile_size, y * self.tile_size)
        item.setZValue(1)
        self.scene.addItem(item)
        self.tiles[(z, x, y, world_offset)] = item

    def setupAttribution(self):
        """
        Affiche l'attribution obligatoire © OpenStreetMap contributors
        """

        self.attribution_label = QLabel("© OpenStreetMap contributors", self)
        self.attribution_label.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.7); "
            "padding: 5px; font-size: 10px;"
        )
        self.attribution_label.adjustSize()
        self.attribution_label.move(
            self.width() - self.attribution_label.width() - 10,
            self.height() - self.attribution_label.height() - 10,
        )
