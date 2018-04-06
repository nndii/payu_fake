from urllib.parse import urljoin

import requests
from aiohttp import web

from payu_fake.resources import IPN
from payu_fake.resources import Transaction


async def _make_request(url: str, data: dict = None):
    if data is None:
        data = {}
    requests.post(url, data=data)


async def post3ds(prefix: str, transaction: Transaction):
    url = urljoin(prefix, transaction.back_ref)
    await _make_request(url)


async def ipn(transaction: Transaction, request: web.Request, status: IPN = IPN.finish):
    url = urljoin(request.app['TC_PREFIX'], request.app['IPN_URL'])
    data = {
        'SALEDATE': '12312312',
        'COMPLETE_DATE': 'asdasd',
        'REFNO': transaction.ref_no,
        'REFNOEXT': transaction.order_ref,
        'ORDERNO': 123123123,
        'ORDERSTATUS': status.value,
        'PAYMETHOD': 'OLOLO'
    }
    await _make_request(url, data=data)
