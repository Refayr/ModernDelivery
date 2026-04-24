# infopanel.py
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt


class InfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_item = None
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self.setStyleSheet("background-color: #f5f5f5; border-left: 1px solid #ccc;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Titre
        self.title_label = QLabel("Sélection")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet(
            "color: #333; border-bottom: 2px solid #ddd; padding-bottom: 5px;"
        )
        layout.addWidget(self.title_label)

        # Zone de contenu défilante
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)

        # Placeholder texte
        self.info_text = QLabel(
            "Cliquez sur un élément sur la carte pour voir ses détails."
        )
        self.info_text.setWordWrap(True)
        self.info_text.setStyleSheet("color: #666; padding: 10px;")
        self.content_layout.addWidget(self.info_text)

        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

        # Bouton Fermer
        self.close_btn = QPushButton("Fermer la sélection")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; border: none; padding: 10px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.close_btn.clicked.connect(self.clear_selection)
        layout.addWidget(self.close_btn)

        layout.addStretch()

    def show_details(self, item):
        """Affiche les détails d'un item (Ship ou Seaport)"""
        self.selected_item = item

        # Nettoyage du contenu précédent
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Création des labels dynamiques
        title = QLabel(f"<b>{item.name}</b>")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        self.content_layout.addWidget(title)

        # Informations spécifiques selon le type
        info_lines = []

        if hasattr(item, "id"):
            info_lines.append(f"<b>ID:</b> {item.id}")

        if hasattr(item, "lat") and item.lat is not None:
            info_lines.append(f"<b>Latitude:</b> {item.lat:.4f}")
            info_lines.append(f"<b>Longitude:</b> {item.lon:.4f}")

        if hasattr(item, "speed"):
            info_lines.append(f"<b>Speed:</b> {item.speed} kts")

        if hasattr(item, "destination"):
            info_lines.append(f"<b>Destination:</b> {item.destination}")

        if hasattr(item, "country"):
            info_lines.append(f"<b>Country:</b> {item.country}")

        # Ajout des lignes
        for line in info_lines:
            lbl = QLabel(line)
            lbl.setStyleSheet("padding: 2px 0; color: #444;")
            self.content_layout.addWidget(lbl)

        # Ajout d'une description si disponible
        if hasattr(item, "description") and item.description:
            desc = QLabel(item.description)
            desc.setWordWrap(True)
            desc.setStyleSheet("margin-top: 10px; color: #555; font-style: italic;")
            self.content_layout.addWidget(desc)

        self.info_text.hide()
        self.title_label.setText(f"Details : {item.name}")

    def clear_selection(self):
        """Efface la sélection et remet le texte par défaut"""
        self.selected_item = None
        self.title_label.setText("Selection")
        self.info_text.show()

        # Supprimer les widgets dynamiques
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.content_layout.addWidget(self.info_text)

        # Émettre un signal pour retirer le cadre rouge de la carte
        # if hasattr(self, "selection_cleared_signal"):
        #     self.selection_cleared_signal.emit()
        if (
            hasattr(self, "selection_cleared_callback")
            and self.selection_cleared_callback
        ):
            self.selection_cleared_callback()

    def set_selection_cleared_callback(self, callback):
        """Permet à la carte de savoir qu'il faut retirer le cadre"""
        self.selection_cleared_signal = callback
