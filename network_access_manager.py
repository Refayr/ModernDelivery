import random as rnd
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QObject, Signal


class NetworkAccessManager(QObject):
    """Pool de gestionnaires réseau conforme à la politique OSM"""

    tile_loaded = Signal(str, bytes)  # URL, données

    def __init__(self, parent, max_concurrent=5):
        super().__init__(parent)
        self.max_concurrent = max_concurrent
        self.current_requests = 0
        self.pending_queue = []

        # self.referer_header = "https://github.com/Refayr/ModernDelivery"
        self.user_agent = (
            "ModernDelivery/1.0 (+https://github.com/Refayr/ModernDelivery)"
        )

        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.setTransferTimeout(10000)

    def getNetworkManager(self):
        return self.network_manager

    def requestTile(self, url):
        """
        Limite les requêtes simultanées pour éviter le blocage OSM
        """
        if self.current_requests >= self.max_concurrent:
            # Mettre en file d'attente
            self.pending_queue.append(url)
            return

        self.current_requests += 1
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", self.user_agent.encode())
        request.setRawHeader(b"Accept", b"image/png,image/jpeg,*/*;q=0.8")
        # request.setRawHeader(b"Referer", self.referer_header.encode())

        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handleReply(reply, url))

    def _handleReply(self, reply, url):
        """
        Gère la réponse et libère le compteur
        Lit les headers de cache pour conformité
        """
        # Lire les headers de cache
        cache_control = reply.rawHeader("Cache-Control")
        expires = reply.rawHeader("Expires")
        etag = reply.rawHeader("ETag")

        # Ne PAS envoyer Cache-Control: no-cache
        # Laisser les headers par défaut

        data = reply.readAll()
        self.current_requests -= 1

        # Émettre signal avec données et headers
        self.tile_loaded.emit(url, data)

        # Traiter la file d'attente
        if self.pending_queue:
            next_url = self.pending_queue.pop(0)
            self.requestTile(next_url)

        reply.deleteLater()
