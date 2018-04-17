from urllib.parse import urljoin

import requests
from aiohttp import web

from payu_fake.resources import Transaction
from payu_fake.utils import change_prefix


async def _make_request(url: str, data: dict = None):
    if data is None:
        data = {}
    return requests.post(url, data=data)


async def post3ds(prefix: str, transaction: Transaction):
    url = change_prefix(prefix, transaction.back_ref)
    resp = await _make_request(url)
    return resp.content.decode(), resp.ok


async def ipn(transaction: Transaction, app: web.Application):
    url = urljoin(app['TC_PREFIX'], app['IPN_URL'])
    data = {
        'SALEDATE': '12312312',
        'COMPLETE_DATE': 'asdasd',
        'REFNO': transaction.ref_no,
        'REFNOEXT': transaction.order_ref,
        'ORDERNO': 123123123,
        'ORDERSTATUS': transaction.status.value,
        'PAYMETHOD': 'OLOLO',
        'IPN_PID[]': 'OMG',
        'IPN_PNAME[]': 'ticket',
        'IPN_DATE': '1231231245'
    }
    print(f'IPN -> {data}')
    await _make_request(url, data=data)
