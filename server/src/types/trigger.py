from pydantic import BaseModel
from typing import Union


class Trigger(BaseModel):
    requestKey: Union[str, None] = None
    direction: Union[str, None] = None
    price: Union[float, None] = None
    pair: Union[str, None] = None
    source: Union[str, None] = None
