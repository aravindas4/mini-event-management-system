from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySQLConfig(BaseSettings):
    """
    MySQL Configuration
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = Field(default="localhost", validation_alias="MYSQL_HOST")
    port: int = Field(default=3306, validation_alias="MYSQL_PORT")
    user: str = Field(default="root", validation_alias="MYSQL_USER")
    password: str = Field(default="", validation_alias="MYSQL_PASSWORD")
    db: str = Field(default="event_management", validation_alias="MYSQL_DATABASE")

    def url(self) -> str:
        """
        Returns the URL for the MySQL database
        """
        return f"mysql+mysqldb://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class DatabaseSettings(BaseSettings):
    """
    Main database settings container
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    primary: MySQLConfig = Field(default_factory=MySQLConfig)


db_settings = DatabaseSettings()