import requests_async as requests
from datetime import datetime, timedelta
from decimal import *

from src.settings import settings
from src.utils.logging import structlog

logger = structlog.getLogger(__name__)


def create_base_headers():
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {settings.oanda_api_key}",
    }


async def create_order(pair, direction):
    r = await requests.post(
        f"{settings.oanda_base_url}/v3/accounts/{settings.oanda_account_id}/orders",
        json=create_open_order_request_body(pair, direction),
        headers=create_base_headers(),
    )
    body = r.json()

    try:
        return body["orderCreateTransaction"]["id"]
    except:
        logger.error("Error placing order", response_body=body)


def create_open_order_request_body(pair, direction):
    instrument = f"{pair[:3]}_{pair[3:]}"
    take_profit_distance = "0.02" if "JPY" in pair else "0.0002"

    return {
        "order": {
            "type": "MARKET",
            "instrument": instrument,
            "units": "15000" if direction == "BUY" else "-15000",
            "timeInForce": "FOK",
            "positionFill": "OPEN_ONLY",
            "takeProfitOnFill": {"distance": take_profit_distance},
        }
    }
