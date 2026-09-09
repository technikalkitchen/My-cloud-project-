from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:

    environment: str = os.getenv(
        "APP_ENV",
        "development"
    )

    timezone: str = os.getenv(
        "APP_TIMEZONE",
        "UTC"
    )

    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


def get_settings() -> Settings:
    return Settings()
