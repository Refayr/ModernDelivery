from abc import ABC, abstractmethod
from typing import Optional, Any
from shapely import wkb  # Pour lire le WKB (Well-Known Binary) retourné par Qt
from shapely.geometry import Point


class AbstractItem(ABC):
    def __init__(self, id="", name="", wkb_geometry: Optional[bytes] = None):
        self.initValues(id, name, wkb_geometry)

    def initValues(self, id: str, name: str, wkb_geometry: Optional[bytes]):
        self.id = id
        self.name = name

        # Conversion du binaire Qt en objet Shapely Point
        try:
            # wkb.loads gère le format WKB standard retourné par PostGIS
            self.geometry = wkb.loads(wkb_geometry)
        except Exception as e:
            print(f"WKB parsing error for {id}: {e}")
            self.geometry = None

    def __eq__(self, other):
        return self.id == other.id

    @property
    def wkb_geometry(self) -> Optional[Point]:
        """Retourne l'objet Point Shapely (géométrie)"""
        return self.geometry

    @property
    def lat(self) -> Optional[float]:
        """Retourne la latitude extraite de la géométrie"""
        if self.geometry is not None:
            return self.geometry.y
        return None

    @lat.setter
    def lat(self, value: float):
        """Met à jour la géométrie avec la nouvelle latitude"""
        if self.geometry is None:
            self.geometry = Point(0.0, value)
        else:
            # On recrée le point car Shapely est immutable
            self.geometry = Point(self.geometry.x, value)

    @property
    def lon(self) -> Optional[float]:
        """Retourne la longitude extraite de la géométrie"""
        if self.geometry is not None:
            return self.geometry.x
        return None

    @lon.setter
    def lon(self, value: float):
        """Met à jour la géométrie avec la nouvelle longitude"""
        if self.geometry is None:
            self.geometry = Point(value, 0.0)
        else:
            self.geometry = Point(value, self.geometry.y)

    def toWkb(self) -> Optional[bytes]:
        """
        Convertit la géométrie interne en binaire WKB pour l'insertion dans QtSql.
        Nécessaire pour faire un UPDATE ou INSERT de la colonne wkb_geometry.
        """
        if self.geometry is None:
            return None
        # Retourne le binaire standard WKB
        return wkb.dumps(self.geometry)

    def geometryToTile(self, wkb_geometry, zoom):
        """
        Convertit une géométrie WKB (Shapely Point) en coordonnées de tuile (x, y).

        Args:
            wkb_geometry: Un objet Point Shapely ou des données WKB binaires
            zoom: Niveau de zoom de la tuile (int)

        Returns:
            tuple: (x_tile, y_tile) coordonnées de la tuile

        Raises:
            ValueError: Si la géométrie est None ou invalide
        """
        # 1. Gérer le cas où wkb_geometry est des données binaires WKB
        if isinstance(wkb_geometry, bytes):
            try:
                wkb_geometry = wkb.loads(wkb_geometry)
            except Exception as e:
                raise ValueError(f"Impossible de parser le WKB: {e}")

        # 2. Vérifier que c'est bien un objet géométrique valide
        if wkb_geometry is None:
            raise ValueError("La géométrie ne peut pas être None")

        # 3. Extraire les coordonnées (Shapely: x=longitude, y=latitude)
        if hasattr(wkb_geometry, "x") and hasattr(wkb_geometry, "y"):
            # Cas d'un Point Shapely
            lon = wkb_geometry.x
            lat = wkb_geometry.y
        elif hasattr(wkb_geometry, "coords"):
            # Cas d'une géométrie avec plusieurs coordonnées (Polygon, LineString)
            # On prend le premier point
            coords = list(wkb_geometry.coords)
            if len(coords) == 0:
                raise ValueError("La géométrie ne contient aucune coordonnée")
            lon, lat = coords[0]
        else:
            raise ValueError(f"Type de géométrie non supporté: {type(wkb_geometry)}")

        # 4. Utiliser la méthode latLonToTile existante
        return self.latLonToTile(lat, lon, zoom)

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

    def tileToLatLon(self, x_tile, y_tile, zoom):
        """
        Convertit les coordonnées de tuile (x, y) en latitude/longitude.
        Méthode inverse de latLonToTile.
        """
        n = 2**zoom
        lon = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat = math.degrees(lat_rad)
        return lat, lon

    def getTileBounds(self, x_tile, y_tile, zoom):
        """
        Retourne les limites (min_lon, min_lat, max_lon, max_lat) d'une tuile.
        Utile pour les requêtes spatiales (ex: trouver tous les navires dans une tuile).
        """
        min_lon, min_lat = self.tileToLatLon(x_tile, y_tile, zoom)
        max_lon, max_lat = self.tileToLatLon(x_tile + 1, y_tile + 1, zoom)
        return min_lon, min_lat, max_lon, max_lat

    def __eq__(self, other):
        if not isinstance(other, AbstractItem):
            return False
        return self.id == other.id

    @staticmethod
    def parseCoordinate(coord_str):
        """
        Convertit '43.3617N' ou '8.3826W' en décimal
        """
        match = re.match(r"([\d.]+)([NSEW])", coord_str.strip())
        if not match:
            return None

        value = float(match.group(1))
        direction = match.group(2)

        if direction in ["S", "W"]:
            return -value
        return value

    # @abstractmethod
    # def abstract(self):
    #     pass
