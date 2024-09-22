from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, validator, field_validator


class StrategyTypes(str, Enum):
    all = 'ALL'
    important = 'IMPORTANT'
    small = 'SMALL'


class RoutingIntent(BaseModel):
    destinationName: str
    important: Optional[bool] = None
    bytes: Optional[int] = None
    score: Optional[int] = None


class EventInputSchema(BaseModel):
    payload: Dict
    routingIntents: List[RoutingIntent]
    strategy: Optional[Union[StrategyTypes, str]] = None

    @field_validator('routingIntents')
    def routing_intents_validator(cls, value: List):
        if not value:
            raise ValueError('Empty field')
        return value

    @field_validator('strategy')
    def strategy_validator(cls, value: str):
        strategy_types = iter(StrategyTypes)
        if value in strategy_types or cls.check_custom_filter_function(value):
            print('True')
        else:
            print('False')
        print(value)
        return value

    @staticmethod
    def check_custom_filter_function(value):
        return False

#  https://regex101.com/r/qMKAbA/1
# compile()
# exec()
# eval("__import__('os').popen('ls').read()")