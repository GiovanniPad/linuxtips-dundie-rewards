import os

SMTP_HOST: str = "localhost"
SMTP_PORT: int = 8025
SMTP_TIMEOUT: int = 5
EMAIL_FROM: str = "master@dundie.com"


ROOT_PATH: str = os.path.dirname(__file__)
DATABASE_PATH: str = os.path.join(ROOT_PATH, "..", "assets", "database.db")
SQL_CON_STRING: str = f"sqlite:///{DATABASE_PATH}"

DATEFMT: str = "%d/%m/%Y %H:%M:%S"

API_BASE_URL = "https://economia.awesomeapi.com.br/json/last/USD-{currency}"

ADMIN_EMAIL = "michael@dundermifflin.com"
KEYRING_SERVICE_NAME = "Dundie"
KEYRING_USERNAME = "logged_user"
