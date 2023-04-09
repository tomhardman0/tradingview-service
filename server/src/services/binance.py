import hmac
import hashlib
from urllib.parse import urlencode
import requests_async as requests
from datetime import datetime, timedelta
from decimal import *

from src.settings import settings
from src.utils.logging import structlog

logger = structlog.getLogger(__name__)


def create_signature(request_params):
    return hmac.new(settings.binance_api_secret.encode(),
                    request_params.encode(), hashlib.sha256).hexdigest()


def calc_take_profit_price(price, direction):
    profit_distance = 0.2
    return price + profit_distance if direction == "BUY" else price - profit_distance


def create_order_request_params(direction, pair, quantity, price, take_profit_price):
    return urlencode({
        "type": "TAKE_PROFIT_LIMIT",
        "side": direction,
        "symbol": pair,
        "timeInForce": "FOK",
        "quantity": quantity,
        "price": price,
        "stopPrice": take_profit_price,
        "recvWindow": 10000,  # good for 10 seconds. May actually be too much in crypto
        "timestamp": int(datetime.now().timestamp() * 1000)
    })


def create_base_headers():
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json; charset=UTF-8",
        "X-MBX-APIKEY": settings.binance_api_key,
    }


async def create_margin_order(pair, direction, price):
    req_params = create_margin_order_request_params(pair, direction, price)

    r = await requests.post(
        f"{settings.binance_base_url}/sapi/v1/margin/order?{req_params}",
        headers=create_base_headers(),
    )
    body = r.json()

    try:
        return body["orderId"]
    except:
        logger.error("Error placing order", response_body=body)


async def create_spot_order(pair, direction, price):
    req_params = create_spot_order_request_params(pair, direction, price)

    r = await requests.post(
        f"{settings.binance_base_url}/v3/order?{req_params}",
        headers=create_base_headers(),
    )
    body = r.json()

    try:
        return body["orderId"]
    except:
        logger.error("Error placing order", response_body=body)


async def get_account_information():
    params = urlencode({
        "timestamp": int(datetime.now().timestamp() * 1000)
    })

    r = await requests.get(
        f"{settings.binance_base_url}/v3/account?{params}&signature={create_signature(params)}",
        headers=create_base_headers(),
    )

    return r.json()


def create_margin_order_request_params(pair, direction, price):
    margin_rate = 10
    margin_order_size = settings.crypto_order_size * margin_rate
    quantity = round(margin_order_size / price, 5)

    params = create_order_request_params(
        direction, pair, quantity, price, calc_take_profit_price(price, direction))

    return f"{params}&signature={create_signature(params)}"


def create_spot_order_request_params(pair, direction, price):
    quantity = round(settings.crypto_order_size / price, 5)

    params = create_order_request_params(
        direction, pair, quantity, price, calc_take_profit_price(price, direction))

    return f"{params}&signature={create_signature(params)}"
