import hashlib
import hmac
import secrets
import typing

from aiohttp import web


async def check_hmac(params: typing.Mapping, secret: str) -> bool:
    hash_source = params['ORDER_HASH']
    hash_calc = await calc_hash(params, secret)
    print(f'HASH SOURCE {hash_source}')
    print(f'HASH CALC {hash_calc}')
    return hash_source == hash_calc


async def calc_hash(data: typing.Mapping, secret: str) -> str:
    sorted_keys = sorted((key for key in data.keys() if key != 'ORDER_HASH'))
    print(f'HASH SORTED KEYS {sorted_keys}')

    body = ''
    for key in sorted_keys:
        value = str(data[key])
        body += str(len(value.encode('utf8'))) + value

    hash_calc = hmac.HMAC(
        key=secret.encode('utf-8'),
        msg=body.encode('utf-8'),
        digestmod=hashlib.md5
    ).hexdigest()

    return hash_calc


def generate_id(request: web.Request) -> int:
    while True:
        temp_id = secrets.randbelow(3333) + 1
        if temp_id not in request.app['t_db']:
            return temp_id
