from abc import ABC, abstractmethod


class AbstractItem(ABC):
    def __init__(self, id="", name="", lat=0.0, lon=0.0):
        self.initValues(id, name, lat, lon)

    def initValues(self, id: str, name: str, lat: float, lon: float):
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
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
