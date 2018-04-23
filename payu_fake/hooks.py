import typing

from aiohttp import web

from payu_fake.client import post3ds, ipn
from payu_fake.resources import Transaction, Status, ReturnCode
from payu_fake.utils import generate_id, check_hmac
from payu_fake.resources import IPN


async def process_alu(request: web.Request) -> \
        typing.Tuple[typing.Union[str, None], Status, ReturnCode]:
    params = await request.post()
    secret = request.app['SECRET']
    ref_id = generate_id(request)
    if not await check_hmac(params, secret):
        return None, Status.error, ReturnCode.some_error

    transaction = Transaction(
        ref_no=str(ref_id),
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
        exp_month=params.get('EXP_MONTH'),
        exp_year=params.get('EXP_YEAR'),
        cc_number=params.get('CC_NUMBER'),
        cc_owner=params.get('CC_OWNER'),
        cc_cvv=params.get('CC_CVV'),
        client_ip=params.get('CLIENT_IP'),
        test_order=params.get('TESTORDER'),
        status=IPN.executed
    )

    request.app['t_db'][transaction.order_ref] = transaction
    _3ds, _idn = map(int, transaction.cc_owner.split(':'))

    if _3ds:
        response = await transaction.xmlify(
            secret, Status.success, ReturnCode.need3ds,
            _3ds=True, _3ds_url='http://nettakogosaita.tochno'
        )
        request.app['3ds'].put(transaction)
        return response, Status.success, ReturnCode.need3ds
    else:
        if not _idn:
            status, return_code = Status.success, ReturnCode.success
        else:
            status, return_code = Status.success, ReturnCode.authorized

        response = await transaction.xmlify(
            secret, status, return_code
        )
        return response, status, return_code


async def process_3ds(app: web.Application, transaction: Transaction):
    response_body, status = await post3ds(app['TC_PREFIX'], transaction)
    if status:
        payment_id = transaction.order_ref.split(':')[-1]
        app['finish'][payment_id] = response_body
    app['ipn'].put(transaction.replace(status=IPN.finish))


async def process_ipn(app: web.Application, transaction: Transaction):
    await ipn(transaction, app)


async def process_idn(request: web.Request) -> \
    typing.Tuple[typing.Union[str, None], Status, ReturnCode]:

    params = await request.post()
    secret = request.app['SECRET']
    if not await check_hmac(params, secret):
        return None, Status.error, ReturnCode.some_error

    try:
        transaction = request.app['t_db'][params.get('ORDER_REF')]
    except KeyError:
        return None, Status.error, ReturnCode.some_error

    response = await transaction.xmlify_inline(
        secret, Status.success, ReturnCode.success
    )
    request.app['ipn'].put(transaction.replace(status=IPN.finish))
    return response, Status.success, ReturnCode.success



