import os


HOST = os.getenv(
    "APP_HOST",
    "0.0.0.0",
)


PORT = int(
    os.getenv(
        "APP_PORT",
        "5000",
    )
)


DEBUG = os.getenv(
    "APP_DEBUG",
    "0",
) == "1"
