from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QCheckBox,
    QSpinBox,
    QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlDatabase

from db_credentials import CredentialStorage
from db_connector import PostGISConnector


class DBLoginDialog(QDialog):
    """Widget de connexion à la base PostGIS"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.credentials_storage = CredentialStorage()
        self.setupUi()
        self.loadSavedCredentials()

    def setupUi(self):
        self.setWindowTitle("PostGIS connection")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Vérifier le driver
        drivers = QSqlDatabase.drivers()
        if "QPSQL" not in drivers:
            warning = QLabel("⚠️ PostgreSQL driver (QPSQL) not detected!")
            warning.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(warning)

        # Groupe de formulaire
        form_group = QGroupBox("Connection credentials")
        form_layout = QFormLayout(form_group)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("localhost")
        form_layout.addRow("Host:", self.host_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        form_layout.addRow("Port:", self.port_input)

        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("db_name")
        form_layout.addRow("Database:", self.database_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("postgres")
        form_layout.addRow("User:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("••••••••")
        form_layout.addRow("Password:", self.password_input)

        self.save_credentials_check = QCheckBox("Save credentials")
        self.save_credentials_check.setChecked(True)
        form_layout.addRow("", self.save_credentials_check)

        layout.addWidget(form_group)

        # Boutons
        button_layout = QHBoxLayout()

        self.test_button = QPushButton("Test connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.ok_button = QPushButton("Connect")
        self.ok_button.clicked.connect(self.accept_connection)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    def loadSavedCredentials(self):
        success, result = self.credentials_storage.load_credentials()
        if success:
            self.host_input.setText(result["host"])
            self.port_input.setValue(result["port"])
            self.database_input.setText(result["database"])
            self.username_input.setText(result["username"])
            self.password_input.setText(result["password"])
            self.status_label.setText("✅ Credentials loaded")

    def getCredentials(self):
        return {
            "host": self.host_input.text().strip(),
            "port": self.port_input.value(),
            "database": self.database_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
        }

    def validateCredentials(self, creds):
        required_fields = ["host", "port", "database", "username", "password"]
        for field in required_fields:
            if not creds.get(field):
                return False, f"Required field '{field}'"
        return True, None

    def testConnection(self):
        creds = self.getCredentials()
        valid, error = self.validateCredentials(creds)
        if not valid:
            QMessageBox.warning(self, "Error", error)
            return

        connector = PostGISConnector(creds)
        success, msg = connector.connect()

        if success:
            connector.disconnect()
            self.status_label.setText("✅ Connection established!")
            QMessageBox.information(
                self, "Succes", "Connection established to the database!"
            )

            if self.save_credentials_check.isChecked():
                save_success, save_msg = self.credentials_storage.saveCredentials(
                    **creds
                )
                if save_success:
                    self.status_label.setText(f"✅ {save_msg}")
        else:
            self.status_label.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)

    def acceptConnection(self):
        creds = self.getCredentials()
        valid, error = self.validateCredentials(creds)
        if not valid:
            QMessageBox.warning(self, "Error", error)
            return

        connector = PostGISConnector(creds)
        success, msg = connector.connect()

        if success:
            connector.disconnect()
            if self.save_credentials_check.isChecked():
                self.credentials_storage.saveCredentials(**creds)
            self.accept()
        else:
            self.status_label.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)
