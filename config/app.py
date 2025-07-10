from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings.

    Environment values:
    - ENV: Current environment (test, dev, prod)
    - DEBUG: Enable debug mode with full stacktraces
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    APP_ENV: str = Field(
        default="production",
        description="Current environment (test, dev, prod)",
        validation_alias="APP_ENV",
    )

    # Debug
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode with full stacktraces",
        validation_alias="DEBUG",
    )

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled either explicitly or by environment"""
        return self.DEBUG or self.APP_ENV.lower() in ["development", "dev", "debug"]
