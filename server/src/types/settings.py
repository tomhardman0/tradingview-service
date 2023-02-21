from pydantic import BaseSettings


class Settings(BaseSettings):
    # expected in .env
    request_key: str = "topsecretkey"
    broker_username: str = "macondorivers1demo"
    broker_password: str
    broker_api_key: str
    broker_account_id: str
    broker_base_url: str = "https://demo-api.ig.com/gateway/deal"
    order_size: float = 1
    order_tolerance: float = 0.2

    # populated dynamically at startup
    security_token: str = ""
    cst: str = ""

    class Config:
        env_file = ".env"
