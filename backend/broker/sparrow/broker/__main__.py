import asyncio
import sys
from os import environ

from hypercorn.asyncio import serve
from hypercorn.config import Config

from . import BrokerConfigError, BrokerSettings, create_app


def main():
    try:
        settings = BrokerSettings.from_env()
    except BrokerConfigError as err:
        sys.exit(f"sparrow-identity-broker: {err}")
    config = Config()
    config.bind = [environ.get("SPARROW_BROKER_BIND", "0.0.0.0:8000")]
    asyncio.run(serve(create_app(settings), config))


if __name__ == "__main__":
    main()
