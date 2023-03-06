from fastapi import HTTPException, Request

from src.settings import settings
from src.utils.logging import structlog
from src.types.trigger import Trigger
from src.services import ig
from src.utils.timing import should_order

logger = structlog.getLogger(__name__)


async def otc_handler(trigger: Trigger, request: Request):
    request_key = trigger.requestKey
    direction = trigger.direction
    price = trigger.price
    pair = trigger.pair
    source = trigger.source

    if request_key is None or request_key != settings.request_key:
        raise HTTPException(status_code=401)

    if direction not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400)

    if price is None:
        raise HTTPException(status_code=400)

    if pair is None:
        raise HTTPException(status_code=400)

    if should_order():
        logger.info(
            "Placing order",
            request_id=request.state.id,
            direction=direction,
            price=price,
            pair=pair,
            source=source,
        )
        deal_reference = await ig.create_order(pair, direction, price)
        logger.info(
            "Order placed", request_id=request.state.id, deal_reference=deal_reference
        )

        return {"status": 200, "dealReference": deal_reference}
    else:
        logger.info(
            "Not ordering: market opening or end of week",
            request_id=request.state.id,
            direction=direction,
            price=price,
            pair=pair,
        )

        return {"status": 200}


async def reauth_handler(trigger: Trigger, request: Request):
    request_key = trigger.requestKey

    if request_key is None or request_key != settings.request_key:
        raise HTTPException(status_code=401)

    settings.security_token = ""
    settings.cst = ""

    logger.info("Reauthenticating", request_id=request.state.id)
    security_token, cst = await ig.get_credentials(request)
    settings.security_token = security_token
    settings.cst = cst
    logger.info("Updated auth headers", request_id=request.state.id)

    return {"status": 200}
