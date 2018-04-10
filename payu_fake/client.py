from urllib.parse import urljoin

import requests
from aiohttp import web

from payu_fake.resources import IPN
from payu_fake.resources import Transaction


async def _make_request(url: str, data: dict = None):
    if data is None:
        data = {}
    resp = requests.post(url, data=data)
    print(f'TC RESP <- {resp.text}')


async def post3ds(prefix: str, transaction: Transaction):
    url = urljoin(prefix, transaction.back_ref)
    await _make_request(url)


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
