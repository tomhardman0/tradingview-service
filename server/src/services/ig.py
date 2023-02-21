from fastapi import Request
import requests_async as requests
from datetime import datetime, timedelta
from typing import Union

from src.settings import settings
from src.utils.logging import structlog
from src.types.settings import Settings

BASE_URL = settings.broker_base_url
PAIR_MAP = {
    "GBPUSD": {"epic": "CS.D.GBPUSD.TODAY.IP", "multiplier": 10000},
    "GBPJPY": {"epic": "CS.D.GBPJPY.TODAY.IP", "multiplier": 100},
    "EURUSD": {"epic": "CS.D.EURUSD.TODAY.IP", "multiplier": 10000},
    "EURGBP": {"epic": "CS.D.EURGBP.TODAY.IP", "multiplier": 10000},
    "EURJPY": {"epic": "CS.D.EURJPY.TODAY.IP", "multiplier": 100},
    "AUDUSD": {"epic": "CS.D.AUDUSD.TODAY.IP", "multiplier": 10000},
    "USDJPY": {"epic": "CS.D.USDJPY.TODAY.IP", "multiplier": 100},
    "USDCAD": {"epic": "CS.D.USDCAD.TODAY.IP", "multiplier": 10000},
    "USDCHF": {"epic": "CS.D.USDCHF.TODAY.IP", "multiplier": 10000},
}
logger = structlog.getLogger(__name__)


def create_base_headers(settings: Settings):
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json; charset=UTF-8",
        "X-IG-API-KEY": settings.broker_api_key,
        "IG-ACCOUNT-ID": settings.broker_account_id,
        "X-SECURITY-TOKEN": settings.security_token,
        "CST": settings.cst,
    }


async def get_credentials(request: Union[Request, None] = None):
    payload = {
        "identifier": settings.broker_username,
        "password": settings.broker_password,
    }
    headers = {**create_base_headers(settings), "Version": "2"}

    try:
        r = await requests.post(
            f"{settings.broker_base_url}/session", json=payload, headers=headers
        )
        headers = r.headers
        return headers["X-SECURITY-TOKEN"], headers["CST"]
    except Exception as e:
        logger.error(
            "Could not authenticate, removing old headers",
            request_id=None if request is None else request.state.id,
            error=repr(e),
        )
        return "", ""


async def create_order(pair, direction, price):
    headers = {
        **create_base_headers(settings),
        "Version": "2",
    }

    r = await requests.post(
        f"{settings.broker_base_url}/workingorders/otc",
        json=create_open_order_request_body(pair, direction, price),
        headers=headers,
    )
    body = r.json()
    return body["dealReference"]


def create_open_order_request_body(pair, direction, price):
    pair_data = PAIR_MAP.get(pair)
    normalised_price = round(price * pair_data.get("multiplier"), 1)
    good_till_date = (datetime.now() + timedelta(seconds=10)).strftime(
        "%Y/%m/%d %H:%M:%S"
    )

    tolerance = settings.order_tolerance
    price_with_tolerance = (
        normalised_price - tolerance
        if direction == "BUY"
        else normalised_price + tolerance
    )

    return {
        "epic": pair_data.get("epic"),
        "expiry": "DFB",
        "direction": direction,
        "size": settings.order_size,
        "type": "LIMIT",
        "level": price_with_tolerance,
        "guaranteedStop": False,
        "stopLevel": None,
        "stopDistance": None,
        "forceOpen": True,
        "limitLevel": None,
        "limitDistance": 2,
        "currencyCode": "GBP",
        "timeInForce": "GOOD_TILL_DATE",
        "goodTillDate": good_till_date,
    }
