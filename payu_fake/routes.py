import asyncio

from aiohttp import web

from payu_fake.hooks import process_alu, process_idn


async def alu(request):
    response, status, return_code = await asyncio.shield(process_alu(request))
    response_obj = web.Response(text=response)
    response_obj.headers['Content-Type'] = 'application/xml'
    return response_obj


async def idn(request):
    response, status, return_code = await asyncio.shield(process_idn(request))
    response_obj = web.Response(text=response)
    response_obj.headers['Content-Type'] = 'application/xml'
    
    return response_obj


async def check_finished(request):
    p_id = request.match_info.get('p_id', 'OMG')
    if str(p_id) in request.app['finish']:
        return web.Response(text=request.app['finish'][p_id], status=200)
    else:
        return web.Response(text='OMG', status=400)


async def omg(request):
    return 'aDASDASDSD'


def setup(app):
    url = app.router

    url.add_post('/order/alu/v3', alu)
    url.add_post('/order/idn.php', idn)
    url.add_get('/check_finished/{p_id}', check_finished)
    # url.add_post('/order/irn.php', irn)
    url.add_get('/', omg)
