from fastapi import FastAPI, Request
import time
from uuid import uuid4

from src.settings import settings
from src.utils.logging import structlog
from src.types.trigger import Trigger
from src.services import ig as ig_api
from src.routes import ig as ig_routes

logger = structlog.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def pre_authenticate():
    logger.info("Setting initial authentication")
    security_token, cst = await ig_api.get_credentials()
    settings.security_token = security_token
    settings.cst = cst
    logger.info("Authenticated")


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = time.time()
    request.state.id = uuid4()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "Request complete", request_id=request.state.id, time_taken_s=process_time
    )
    return response


@app.post("/ig/otc")
async def ig_otc(trigger: Trigger, request: Request):
    return await ig_routes.otc_handler(trigger, request)


@app.post("/ig/reauth")
async def ig_reauth(trigger: Trigger, request: Request):
    return await ig_routes.reauth_handler(trigger, request)
