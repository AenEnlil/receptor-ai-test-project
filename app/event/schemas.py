import re
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, field_validator
from app.utils import check_if_syntax_is_correct, check_for_dangerous_code


class StrategyTypes(str, Enum):
    all = 'all'
    important = 'important'
    small = 'small'


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

        if value not in strategy_types and not cls.check_custom_filter_function(value):
            raise ValueError('strategy type error')
        return value

    @staticmethod
    def check_custom_filter_function(value):

        pattern = r"lambda +(\w*) *: *\[(.+)\]"
        if not re.match(pattern, value):
            print('not matched')
            return False

        pattern = r"\[(.+)\]"
        comprehension = re.search(pattern, value)

        if not comprehension:
            print('wrong comrehension')
            return False

        comprehension = comprehension.group(0)

        if not check_for_dangerous_code(comprehension):
            print('dangerous code')
            return False

        if not check_if_syntax_is_correct(value):
            print('syntax error')
            return False

        return True
