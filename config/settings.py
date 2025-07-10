from .app import AppSettings
from .database import DatabaseSettings


class Settings:
    app = AppSettings()
    db = DatabaseSettings()


settings = Settings()
