import numpy as np
import heapq
import math
import time
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from typing import List, Tuple, Optional, Dict
import psycopg2
from psycopg2.extras import RealDictCursor

# --- CONFIGURATION ---
GRID_RESOLUTION = 0.5  # 0.1 degré (~11km). Plus petit = plus précis mais plus lent.
MAX_ITERATIONS = 5000  # Limite de recherche pour éviter les boucles infinies
UPDATE_INTERVAL = 30  # Secondes


class FastShipRouter:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.grid_cache = None
        self.obstacles = []
        self.last_update = 0

        # Chargement initial des obstacles (Continents + Zones interdites)
        self._load_obstacles()
        self._build_grid()

    def _load_obstacles(self):
        """Charge les polygones de continents et zones interdites depuis la DB"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Supposons une table 'continents' et 'no_go_zones' avec une colonne 'geom' (Polygon/MultiPolygon)
        # Si vous n'avez pas ces tables, vous pouvez charger un fichier GeoJSON ici.
        query = """
            SELECT ST_Collect(geom) as geom FROM (
                SELECT geom FROM continents
                UNION ALL
                SELECT geom FROM no_go_zones
            ) as combined
        """
        cur.execute(query)
        result = cur.fetchone()

        if result and result["geom"]:
            # Fusionner tous les polygones en un seul MultiPolygon pour accéler les tests
            self.obstacles = [result["geom"]]
        else:
            print("⚠️ Aucun obstacle trouvé. Tous les océans sont navigables.")
            self.obstacles = []

        cur.close()
        conn.close()

    def _build_grid(self):
        """
        Génère une grille binaire (numpy array) où 1 = obstacle, 0 = eau.
        Cette opération est lourde mais ne se fait qu'une fois au démarrage.
        """
        print("🏗️ Construction de la grille de navigation...")

        # Définir les bornes globales (Monde)
        min_lon, min_lat = -180, -90
        max_lon, max_lat = 180, 90

        cols = int((max_lon - min_lon) / GRID_RESOLUTION)
        rows = int((max_lat - min_lat) / GRID_RESOLUTION)

        # Initialiser la grille (0 = eau)
        grid = np.zeros((rows, cols), dtype=np.uint8)

        # Pour chaque cellule, vérifier si elle touche un obstacle
        # Optimisation : On ne teste que les cellules proches des côtes si possible,
        # mais ici on fait une boucle simple pour la robustesse.

        # Conversion des obstacles en formes Shapely
        obstacle_shapes = []
        for obs in self.obstacles:
            if obs.geom_type == "MultiPolygon":
                obstacle_shapes.extend(obs.geoms)
            else:
                obstacle_shapes.append(obs)

        total_cells = rows * cols
        print(f"   Grille: {cols}x{rows} ({total_cells} cellules)")

        for r in range(rows):
            lat = max_lat - (r + 0.5) * GRID_RESOLUTION
            for c in range(cols):
                lon = min_lon + (c + 0.5) * GRID_RESOLUTION

                # Test rapide : est-ce que le point central est dans un obstacle ?
                pt = Point(lon, lat)
                for shape in obstacle_shapes:
                    if shape.contains(pt):
                        grid[r, c] = 1  # Obstacle
                        break

        self.grid_cache = grid
        self.grid_origin = (min_lon, max_lat)  # Coin haut-gauche
        print("✅ Grille construite.")

    def _latlon_to_grid(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convertit Lat/Lon en coordonnées de grille (row, col)"""
        min_lon, max_lat = self.grid_origin
        c = int((lon - min_lon) / GRID_RESOLUTION)
        r = int((max_lat - lat) / GRID_RESOLUTION)

        # Bornes
        r = max(0, min(r, self.grid_cache.shape[0] - 1))
        c = max(0, min(c, self.grid_cache.shape[1] - 1))
        return r, c

    def _grid_to_latlon(self, r: int, c: int) -> Tuple[float, float]:
        """Convertit grille en Lat/Lon (centre de la cellule)"""
        min_lon, max_lat = self.grid_origin
        lon = min_lon + (c + 0.5) * GRID_RESOLUTION
        lat = max_lat - (r + 0.5) * GRID_RESOLUTION
        return lat, lon

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Distance Euclidienne simple (rapide)"""
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def find_shortest_path(
        self, start_lat: float, start_lon: float, end_lat: float, end_lon: float
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Algorithme A* sur la grille.
        Retourne une liste de (lat, lon) ou None si impossible.
        """
        start_node = self._latlon_to_grid(start_lat, start_lon)
        end_node = self._latlon_to_grid(end_lat, end_lon)

        # Vérifier si start/end sont dans un obstacle
        if self.grid_cache[start_node] == 1 or self.grid_cache[end_node] == 1:
            return None

        # File de priorité: (f_score, g_score, node)
        open_set = [(0, 0, start_node)]
        came_from = {}
        g_score = {start_node: 0}

        iterations = 0

        while open_set:
            _, current_g, current = heapq.heappop(open_set)
            iterations += 1

            if iterations > MAX_ITERATIONS:
                print("⚠️ Trop d'itérations, abandon.")
                return None

            if current == end_node:
                # Reconstruction du chemin
                path = []
                while current in came_from:
                    path.append(self._grid_to_latlon(*current))
                    current = came_from[current]
                path.append((start_lat, start_lon))
                path.reverse()
                return path

            # Voisins (8 directions pour diagonales)
            for dr, dc in [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1),
            ]:
                neighbor = (current[0] + dr, current[1] + dc)

                # Vérifier limites et obstacles
                if (
                    0 <= neighbor[0] < self.grid_cache.shape[0]
                    and 0 <= neighbor[1] < self.grid_cache.shape[1]
                    and self.grid_cache[neighbor] == 0
                ):

                    # Distance (diagonale = sqrt(2), orthogonal = 1)
                    dist = 1.414 if dr != 0 and dc != 0 else 1.0
                    tentative_g = (
                        current_g + dist * GRID_RESOLUTION * 111000
                    )  # En mètres approx

                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f_score = (
                            tentative_g
                            + self._heuristic(neighbor, end_node)
                            * GRID_RESOLUTION
                            * 111000
                        )
                        came_from[neighbor] = current
                        heapq.heappush(open_set, (f_score, tentative_g, neighbor))

        return None

    def update_ship_positions(self):
        """
        Récupère les bateaux, calcule le chemin vers leur port,
        avance le bateau de 1 pas (ou met à jour la position future).
        """
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Récupérer les bateaux avec leur port cible
        # Supposons une colonne 'target_port_id' dans la table ships
        query = """
            SELECT s.id, s.wkb_geometry, s.target_port_id,
                   ST_X(s.wkb_geometry) as lon, ST_Y(s.wkb_geometry) as lat
            FROM ships s
            WHERE s.target_port_id IS NOT NULL
        """
        cur.execute(query)
        ships = cur.fetchall()

        updates = []

        for ship in ships:
            ship_id = ship["id"]
            curr_lat = ship["lat"]
            curr_lon = ship["lon"]
            target_port_id = ship["target_port_id"]

            # Récupérer les coordonnées du port cible
            port_query = "SELECT ST_X(wkb_geometry) as lon, ST_Y(wkb_geometry) as lat FROM seaports WHERE id = %s"
            cur.execute(port_query, (target_port_id,))
            port = cur.fetchone()

            if not port:
                continue

            target_lat = port["lat"]
            target_lon = port["lon"]

            # 2. Calculer le chemin
            path = self.find_shortest_path(curr_lat, curr_lon, target_lat, target_lon)

            if path and len(path) > 1:
                # Avancer le bateau d'un pas (ex: 10% du premier segment)
                # Pour simplifier, on prend juste le deuxième point du chemin (prochaine case)
                next_lat, next_lon = path[1]

                # Calculer la distance parcourue (vitesse simulée)
                # Ici on se contente de sauter à la prochaine case de la grille pour la démo
                # Dans un vrai cas, on interpolerait la vitesse.

                updates.append((next_lat, next_lon, ship_id))
            else:
                # Pas de chemin trouvé (bloqué par terre)
                print(f"⚠️ Bateau {ship_id} bloqué ou destination inaccessible.")

        # 3. Mettre à jour la DB
        if updates:
            update_query = """
                UPDATE ships
                SET wkb_geometry = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    last_updated = NOW()
                WHERE id = %s
            """
            cur.executemany(update_query, updates)
            conn.commit()
            print(f"✅ {len(updates)} bateaux mis à jour.")
        else:
            print("ℹ️ Aucun bateau à mettre à jour.")

        cur.close()
        conn.close()


# --- INTÉGRATION DANS L'APPLICATION QT ---


def start_routing_loop(app, db_config):
    """Fonction à appeler depuis ModernDelivery"""
    router = FastShipRouter(db_config)

    def periodic_update():
        router.update_ship_positions()

    timer = QTimer()
    timer.timeout.connect(periodic_update)
    timer.start(UPDATE_INTERVAL * 1000)
    print(f"🚀 Routeur lancé. Mise à jour toutes les {UPDATE_INTERVAL}s.")

    # Lancer la première mise à jour immédiatement
    periodic_update()
