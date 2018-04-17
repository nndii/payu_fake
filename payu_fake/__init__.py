import asyncio
import os
from queue import Queue

from aiohttp import web

from payu_fake.hooks import process_3ds, process_ipn
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


async def check_for_ipn(app: web.Application):
    try:
        await asyncio.sleep(0.01)
        while True:
            if not app['ipn'].empty():
                await process_ipn(app, app['ipn'].get())
            await asyncio.sleep(1.5)
    except asyncio.CancelledError:
        print('Cancel ipn listener..')


async def start_bg_tasks(app: web.Application):
    app['check_for_3ds'] = app.loop.create_task(check_for_3ds(app))
    app['check_for_ipn'] = app.loop.create_task(check_for_ipn(app))


async def cleanup_bg_tasks(app: web.Application):
    print('cleanup background tasks')
    app['check_for_3ds'].cancel()
    app['check_for_ipn'].cancel()


def create_app() -> web.Application:
    app = web.Application()
    setup(app)

    app['IPN_URL'] = os.environ['IPN_URL']
    app['TC_PREFIX'] = os.environ['TC_PREFIX']
    app['SECRET'] = os.environ['PAYU_SECRET']
    app['t_db'] = dict()
    app['3ds'] = Queue()
    app['ipn'] = Queue()
    app['finish'] = dict()

    app.on_startup.append(start_bg_tasks)
    app.on_cleanup.append(cleanup_bg_tasks)
    return app
