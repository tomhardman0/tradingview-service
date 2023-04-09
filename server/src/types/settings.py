from pydantic import BaseSettings


class Settings(BaseSettings):
    # expected in .env
    request_key: str = "topsecretkey"
    ig_username: str
    ig_password: str
    ig_api_key: str
    ig_account_id: str
    ig_base_url: str = "https://demo-api.ig.com/gateway/deal"
    order_size: float = 1
    order_tolerance: float = 0.2

    oanda_api_key: str
    oanda_account_id: str
    oanda_base_url: str

    crypto_order_size: float = 3000  # in USD
    binance_api_key: str
    binance_api_secret: str
    binance_base_url: str

    # populated dynamically at startup
    security_token: str = ""
    cst: str = ""

    class Config:
        env_file = ".env"
