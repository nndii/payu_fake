import datetime
import xml.etree.ElementTree as xml
from enum import Enum
from typing import NamedTuple

from payu_fake.utils import calc_hash


class IPN(Enum):
    finish = 'COMPLETE'
    pre_finish = 'PAYMENT_AUTHORIZED'
    executed = 'EXECUTED'
    refund = 'REFUND'
    reversed = 'REVERSED'


class ReturnCode(Enum):
    authorized = 'AUTHORIZED'
    need3ds = '3DS_ENROLLED'
    success = 'SUCCESS'
    some_error = 'ERROR'


class Status(Enum):
    success = 'SUCCESS'
    fail = 'AUTHORIZATION_FAILED'
    error = 'INPUT_ERROR'


class Transaction(NamedTuple):
    ref_no: str
    alias: str
    merchant: str
    order_ref: str
    order_date: str
    back_ref: str
    order_pname: str
    order_pcode: str
    order_price: str
    order_qty: str
    prices_currency: str
    bill_lname: str
    bill_fname: str
    bill_email: str
    bill_phone: str
    bill_countrycode: str
    cc_number: str
    cc_owner: str
    exp_month: str
    exp_year: str
    cc_cvv: str
    client_ip: str
    test_order: str
    status: IPN
    pay_method: str = 'CCVISAMC'

    def replace(self, **kwargs):
        return self._replace(**kwargs)

    async def xmlify(
        self, secret: str, _status: Status,
        _return_code: ReturnCode, _3ds: bool = False,
        _3ds_url: str = '') -> str:
        # O M G
        root = xml.Element('EPAYMENT')
        ref_no = xml.SubElement(root, 'REFNO')
        ref_no.text = '' if _status == Status.error else self.ref_no
        alias = xml.SubElement(root, 'ALIAS')
        alias.text = str(ref_no.text)
        status = xml.SubElement(root, 'STATUS')
        status.text = _status.value
        return_code = xml.SubElement(root, 'RETURN_CODE')
        return_code.text = _return_code.value
        return_message = xml.SubElement(root, 'RETURN_MESSAGE')
        return_message.text = 'PRIVET'
        date = xml.SubElement(root, 'DATE')
        date.text = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if _3ds:
            url_3ds = xml.SubElement(root, 'url_3ds')
            url_3ds.text = _3ds_url
        order_ref = xml.SubElement(root, 'ORDER_REF')
        order_ref.text = self.order_ref
        auth_code = xml.SubElement(root, 'AUTH_CODE')
        auth_code.text = '13157TUlA15117'

        data = {item.tag: item.text for item in root}
        _hash = await calc_hash(data, secret)

        order_hash = xml.SubElement(root, 'hash')
        order_hash.text = _hash

        return xml.tostring(root).decode()

    async def xmlify_inline(
        self, secret: str, _status: Status,
        _return_code: ReturnCode, _3ds: bool = False,
        _3ds_url: str = '') -> str:
        # O M G
        data = {
            'ORDER_REF': self.order_ref,
            'RESPONSE_CODE': 1,
            'RESPONSE_MSG': 'OMG',
            'IDN_DATE': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        _hash = await calc_hash(data, secret)

        root = xml.Element('EPAYMENT')
        root.text = (f"{data['ORDER_REF']}|"
                     f"{data['RESPONSE_CODE']}|"
                     f"{data['RESPONSE_MSG']}|"
                     f"{data['IDN_DATE']}|"
                     f"{_hash}")
        return xml.tostring(root).decode()
