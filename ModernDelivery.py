import sys
import io
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QWidget,
    QLabel,
)  # , QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QImage
import staticmaps


class StaticMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carte statique avec py-staticmaps et PySide6")
        self.setGeometry(100, 100, 800, 600)

        # Créer un widget central et un layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Ajouter un titre
        layout.addWidget(QLabel("Carte statique avec marqueurs (Paris et Lyon)"))

        # Créer une scène et une vue pour la carte
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        # Générer et afficher la carte statique
        self.generate_static_map()

    def generate_static_map(self):
        # Créer une carte centrée sur la France (46.6034, 2.3522) avec un zoom de 6
        context = staticmaps.Context()
        context.set_tile_provider(staticmaps.tile_provider_OSM)

        # Ajouter un marqueur pour Paris
        paris = staticmaps.create_latlng(48.864716, 2.349014)
        context.add_object(staticmaps.Marker(paris, color=staticmaps.RED, size=10))

        # Ajouter un marqueur pour Lyon
        lyon = staticmaps.create_latlng(45.763420, 4.834277)
        context.add_object(staticmaps.Marker(lyon, color=staticmaps.GREEN, size=10))

        # Ajouter une ligne entre Paris et Lyon
        context.add_object(
            staticmaps.Line([paris, lyon], color=staticmaps.BLUE, width=2)
        )

        # Rendre l'image de la carte
        image = context.render_cairo(800, 500)
        # image.write_to_png("paris_lyon.cairo.png")

        # Convertir l'image PIL en QPixmap pour PySide6
        buffer = io.BytesIO()
        image.write_to_png(buffer)
        buffer.seek(0)

        qimage = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        # Ajouter l'image à la scène
        self.scene.addPixmap(pixmap)


# Lancer l'application
app = QApplication(sys.argv)
window = StaticMapWindow()
window.show()
sys.exit(app.exec())
