import asyncio
import os
import time
import traceback
from importlib import reload
from logging import Logger

import uvicorn
from starlette.applications import Starlette
from uvicorn import Config
from uvicorn.supervisors import StatReload

from blockexp import init_app

__all__ = ["app", "main"]

app: Starlette

RELOAD = False


def main():
    import blockexp

    directory = os.path.dirname(os.path.dirname(__file__))

    reloader = StatReload(Config(
        app=None,
        debug=True,
        reload_dirs=[directory],
    ))

    logger: Logger = reloader.config.logger_instance

    while True:
        uvicorn.run(
            f"{__name__}:app",
            host='0.0.0.0',
            port=8000,
            debug=True and RELOAD,
            reload=RELOAD,
            reload_dirs=[directory],
        )

        if not RELOAD:
            break

        logger.error("FAILURE RELOAD")

        while True:
            time.sleep(0.3)
            if reloader.should_restart():
                reloader.clear()

                # noinspection PyBroadException
                try:
                    reload(blockexp)
                    init_app(debug=True)
                except Exception:
                    traceback.print_exc()
                    logger.error("FAILURE RELOAD")
                else:
                    break


def __getattr__(name):
    if name == "app":
        app = asyncio.run(init_app(debug=True))
        return app.ready()

    raise AttributeError(name)
