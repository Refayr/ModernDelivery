import requests

from PySide6.QtCore import Signal
from mlineedit import MLineEdit
from mlistwidget import MListWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout


<<<<<<< HEAD
def getCoordinatesFromLocation(location_name):
=======
def get_coordinates_from_location(location_name):
>>>>>>> a4a8dd7 (Initial version of the map viewer)
    # Base URL API Nominatim
    base_url = "https://nominatim.openstreetmap.org/search"

    # query parameters
    params = {
        "q": location_name,  # Place name or address
        "format": "json",  # response format (JSON)
        "limit": 10,  # Limit on number of results
    }

    # Browser Impersonation Header (Nominatim required)
    headers = {"User-Agent": "MyGeocodingApp/1.0"}  # Specify your app/version

    # Run GET-request
    response = requests.get(base_url, params=params, headers=headers)

    # Check response status
    if response.status_code == 200:
        data = response.json()

        if data:
            return data
<<<<<<< HEAD
        raise ValueError("Location not found.")

    raise Exception(f"Query error: {response.status_code}")
=======
        else:
            raise ValueError("Location not found.")
    else:
        raise Exception(f"Query error: {response.status_code}")
>>>>>>> a4a8dd7 (Initial version of the map viewer)


class SearchWidget(QWidget):
    changedLocation = Signal(float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(350)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # input field
        self.search_box = MLineEdit(self)
        self.search_box.textChanged.connect(self.changeEditText)
        self.search_box.setFixedSize(350, 30)
        self.search_box.setPlaceholderText("search for a place...")

        layout.addWidget(self.search_box)
        self.setLayout(layout)

<<<<<<< HEAD
        # Store coordinates
        self.location_dict = {}
        self.suggestions = []
=======
        # Хранение координат
        self.location_dict = dict()
        self.suggestions = list()
>>>>>>> a4a8dd7 (Initial version of the map viewer)

        self.suggestList = MListWidget(self.parent())
        self.suggestList.setFixedWidth(350)
        self.suggestList.move(20, 30 + 20)
        self.suggestList.hide()
        self.suggestList.itemClicked.connect(self.onSelection)

        self.search_box.onFocus.connect(self.onActive)
        self.suggestList.outFocus.connect(self.onDeactive)
        self.search_box.outFocus.connect(self.onDeactive)

    def onActive(self):
        if len(self.suggestions):
            self.suggestList.setVisible(True)

    def onDeactive(self):
        if not self.suggestList.hasFocus():
            self.suggestList.setVisible(False)

    def changeEditText(self, text):
        if len(text) <= 3:
            self.suggestList.hide()
            return
        self.suggestList.setVisible(True)

        self.location_dict.clear()  # Clean old data

<<<<<<< HEAD
        ranked_place = []
        mrequest = getCoordinatesFromLocation(text)
=======
        ranked_place = list()
        mrequest = get_coordinates_from_location(text)
>>>>>>> a4a8dd7 (Initial version of the map viewer)
        for place in mrequest:
            place_rank = int(place["place_rank"])
            display_name = place["display_name"]

            print(place)

            self.location_dict[display_name] = place["boundingbox"]
            ranked_place.append((place_rank, display_name))

        ranked_place.sort(reverse=False)

        self.updateSuggestions([place for _, place in ranked_place])

    def updateSuggestions(self, suggestions):
        """Updates the list of suggestions in Complete"""

        self.suggestions = suggestions
        self.suggestList.clear()
        self.suggestList.addItems(suggestions)

    def onSelection(self, item):
        """Process the item selection and returns coordinates"""

        text = item.text()

        boundingbox = self.location_dict.get(text, None)
        if boundingbox:
            print(f"Selected: {text}, coordinates: {boundingbox}")
            if len(boundingbox) != 4:
                print(
                    "Error: boundingbox must contain 4 coordinates (south, north, west, east)"
                )
                return

            # Convert strings to numbers
            south, north, west, east = map(float, boundingbox)
            self.changedLocation.emit(south, north, west, east)
            self.suggestList.hide()
