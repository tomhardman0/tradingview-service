from fastapi import HTTPException, Request

from src.settings import settings
from src.utils.logging import structlog
from src.types.trigger import Trigger
from src.services import binance
from src.utils.timing import should_order

logger = structlog.getLogger(__name__)


async def spot_order_handler(trigger: Trigger, request: Request):
    request_key = trigger.requestKey
    direction = trigger.direction
    price = trigger.price
    pair = trigger.pair

    if request_key is None or request_key != settings.request_key:
        raise HTTPException(status_code=401)

    if direction not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400)

    if price is None:
        raise HTTPException(status_code=400)

    if pair is None:
        raise HTTPException(status_code=400)

    logger.info(
        "Placing order",
        request_id=request.state.id,
        direction=direction,
        price=price,
        pair=pair,
    )
    order_id = await binance.create_spot_order(pair, direction, price)

    if order_id is None:
        raise HTTPException(status_code=500)

    logger.info(
        "Order placed", request_id=request.state.id, deal_reference=order_id
    )

    return {"status": 200, "dealReference": order_id}


async def margin_order_handler(trigger: Trigger, request: Request):
    request_key = trigger.requestKey
    direction = trigger.direction
    price = trigger.price
    pair = trigger.pair

    if request_key is None or request_key != settings.request_key:
        raise HTTPException(status_code=401)

    if direction not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400)

    if price is None:
        raise HTTPException(status_code=400)

    if pair is None:
        raise HTTPException(status_code=400)

    logger.info(
        "Placing order",
        request_id=request.state.id,
        direction=direction,
        price=price,
        pair=pair,
    )
    order_id = await binance.create_margin_order(pair, direction, price)

    if order_id is None:
        raise HTTPException(status_code=500)

    logger.info(
        "Order placed", request_id=request.state.id, deal_reference=order_id
    )

    return {"status": 200, "dealReference": order_id}


async def get_account_information():
    info = await binance.get_account_information()

    return {"status": 200, "info": info}
