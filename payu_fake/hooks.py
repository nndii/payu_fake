import typing

from aiohttp import web

from payu_fake.client import post3ds
from payu_fake.resources import Transaction, Status, ReturnCode
from payu_fake.utils import generate_id, check_hmac


async def process_alu(request: web.Request) -> \
        typing.Tuple[typing.Union[str, None], Status, ReturnCode]:
    params = await request.post()
    secret = request.app['SECRET']
    print(f'ALU <-\n{params}')
    ref_id = generate_id(request)
    if not await check_hmac(params, secret):
        return None, Status.error, ReturnCode.some_error

    transaction = Transaction(
        ref_no=ref_id,
        alias=str(ref_id),
        merchant=params.get('MERCHANT'),
        order_ref=params.get('ORDER_REF'),
        order_date=params.get('ORDER_DATE'),
        pay_method=params.get('PAY_METHOD'),
        back_ref=params.get('BACK_REF'),
        order_pname=params.get('ORDER_PNAME[0]'),
        order_pcode=params.get('ORDER_PCODE[0]'),
        order_price=params.get('ORDER_PRICE[0]'),
        order_qty=params.get('ORDER_QTY[0]'),
        prices_currency=params.get('PRICES_CURRENCY'),
        bill_lname=params.get('BILL_LNAME'),
        bill_fname=params.get('BILL_FNAME'),
        bill_email=params.get('BILL_EMAIL'),
        bill_phone=params.get('BILL_PHONE'),
        bill_countrycode=params.get('BILL_COUNTRYCODE'),
        cc_number=params.get('CC_NUMBER'),
        cc_owner=params.get('CC_OWNER'),
        cc_cvv=params.get('CC_CVV'),
        client_ip=params.get('CLIENT_IP'),
        test_order=params.get('TESTORDER')
    )

    request.app[transaction.ref_no] = transaction
    _3ds = True if transaction.cc_number.endswith('33') else False

    if _3ds:
        response = await transaction.xmlify(
            secret, Status.success, ReturnCode.need3ds,
            _3ds=True, _3ds_url=request.app['3ds_url']
        )
        request.app['3ds'].put(transaction)
        return response, Status.success, ReturnCode.need3ds
    else:
        response = await transaction.xmlify(
            secret, Status.success, ReturnCode.authorized
        )
        return response, Status.success, ReturnCode.authorized


async def process_3ds(app: web.Application, transaction: Transaction):
    await post3ds(app['TC_PREFIX'], transaction)
