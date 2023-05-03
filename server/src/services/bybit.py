from decimal import *
from pybit.unified_trading import HTTP

from src.settings import settings
from src.utils.logging import structlog

logger = structlog.getLogger(__name__)
session = HTTP(
    api_key=settings.bybit_api_key,
    api_secret=settings.bybit_api_secret,
    testnet=settings.env == "staging",
)


async def create_order(pair, direction, price):
    response = session.place_order(
        category="linear",
        symbol=pair.replace(".P", ""),
        side="Buy" if direction == "BUY" else "Sell",
        orderType="Limit",
        qty=f"{calc_contract_quantity(price)}",
        price=f"{price}",
        takeProfit=f"{calc_take_profit_price(price, direction)}",
        timeInForce="IOC",
    )

    try:
        return response["result"]["orderId"]
    except:
        logger.error("Error placing order", response_body=response)


def calc_contract_quantity(price):
    margin_rate = 10
    margin_order_size = settings.crypto_order_size * margin_rate
    return round(margin_order_size / price, 5)


def calc_take_profit_price(price, direction):
    profit_distance = settings.crypto_profit_distance
    return price + profit_distance if direction == "BUY" else price - profit_distance
