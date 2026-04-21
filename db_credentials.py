import keyring


class CredentialStorage:
    """Stockage sécurisé des identifiants de base de données"""

    SERVICE_NAME = "moderndelivery_db"
    USERNAME_KEY = "db_username"
    PASSWORD_KEY = "db_password"
    HOST_KEY = "db_host"
    PORT_KEY = "db_port"
    DATABASE_KEY = "db_database"

    def __init__(self):
        self.keyring_service = self.SERVICE_NAME

    def saveCredentials(self, username, password, host, port, database):
        try:
            keyring.set_password(self.keyring_service, self.USERNAME_KEY, username)
            keyring.set_password(self.keyring_service, self.PASSWORD_KEY, password)
            keyring.set_password(self.keyring_service, self.HOST_KEY, host)
            keyring.set_password(self.keyring_service, self.PORT_KEY, str(port))
            keyring.set_password(self.keyring_service, self.DATABASE_KEY, database)
            return True, "Credentials successfully found"
        except Exception as e:
            return False, f"Save error: {str(e)}"

    def loadCredentials(self):
        try:
            username = keyring.get_password(self.keyring_service, self.USERNAME_KEY)
            password = keyring.get_password(self.keyring_service, self.PASSWORD_KEY)
            host = keyring.get_password(self.keyring_service, self.HOST_KEY)
            port = keyring.get_password(self.keyring_service, self.PORT_KEY)
            database = keyring.get_password(self.keyring_service, self.DATABASE_KEY)

            if all([username, password, host, port, database]):
                return True, {
                    "username": username,
                    "password": password,
                    "host": host,
                    "port": int(port),
                    "database": database,
                }
            return False, "No credential found"
        except Exception as e:
            return False, f"Loading error: {str(e)}"

    def deleteCredentials(self):
        try:
            keyring.delete_password(self.keyring_service, self.USERNAME_KEY)
            keyring.delete_password(self.keyring_service, self.PASSWORD_KEY)
            keyring.delete_password(self.keyring_service, self.HOST_KEY)
            keyring.delete_password(self.keyring_service, self.PORT_KEY)
            keyring.delete_password(self.keyring_service, self.DATABASE_KEY)
            return True, "Credentials deleted"
        except keyring.errors.PasswordDeleteError:
            return True, "No credential to delete"
        except Exception as e:
            return False, f"Delete error: {str(e)}"

    def hasCredentials(self):
        try:
            username = keyring.get_password(self.keyring_service, self.USERNAME_KEY)
            return username is not None
        except:
            return False
