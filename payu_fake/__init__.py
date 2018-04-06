import asyncio
import os
from queue import Queue

from aiohttp import web

from payu_fake.hooks import process_3ds
from payu_fake.routes import setup


async def check_for_3ds(app: web.Application):
    try:
        await asyncio.sleep(0.01)
        while True:
            if not app['3ds'].empty():
                await process_3ds(app, app['3ds'].get())
            await asyncio.sleep(1.5)
    except asyncio.CancelledError:
        print('Cancel 3ds listener..')


async def start_bg_tasks(app: web.Application):
    app['check_for_3ds'] = app.loop.create_task(check_for_3ds(app))


async def cleanup_bg_tasks(app: web.Application):
    print('cleanup background tasks')
    app['check_for_3ds'].cancel()


def create_app() -> web.Application:
    app = web.Application()
    setup(app)

    app['IPN_URL'] = os.environ['IPN_URL']
    app['TC_PREFIX'] = os.environ['TC_PREFIX']
    app['SECRET'] = os.environ['PAYU_SECRET']
    app['TRANSACTION_DB'] = dict()
    app['3ds'] = Queue()

    app.on_startup.append(start_bg_tasks)
    app.on_cleanup.append(cleanup_bg_tasks)
    return app
