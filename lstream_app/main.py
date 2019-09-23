import logging
import sys
import asyncio
import uvloop

from aiohttp import web

from lstream_app.routes import setup_routes
from lib.config import config

from lstream_app.db import init_mongo


def init_app(argv=None):
    logging.basicConfig(level=logging.DEBUG)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app = web.Application()
    app['config'] = config
    setup_routes(app)
    app.on_startup.append(init_mongo)
    return app


def main(argv):

    app = init_app()
    web.run_app(app, host=app['config']['host'], port=app['config']['port'])


if __name__ == '__main__':
    main(sys.argv[1:])
