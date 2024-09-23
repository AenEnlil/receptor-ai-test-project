import re
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, field_validator
from app.utils import check_if_syntax_is_correct, check_for_dangerous_code
from .exceptions import CustomFilterValidationError


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

        try:
            if value not in strategy_types and not cls.check_custom_filter_function(value):
                raise ValueError('strategy type error')
            return value
        except Exception as e:
            raise ValueError(e.args[0])

    @staticmethod
    def check_custom_filter_function(value):
        validation_error_message = 'custom filter validation error'

        pattern = r"lambda +(\w*) *: *\[(.+)\]"
        if not re.match(pattern, value):
            raise CustomFilterValidationError({validation_error_message: 'filter does not match pattern'})

        pattern = r"\[(.+)\]"
        filter_part = re.search(pattern, value)

        if not filter_part:
            raise CustomFilterValidationError({validation_error_message: 'filter expression incorrect'})

        filter_code = filter_part.group(0)

        if not check_for_dangerous_code(filter_code):
            raise CustomFilterValidationError({validation_error_message: 'filter contains dangerous code'})

        if not check_if_syntax_is_correct(value):
            raise CustomFilterValidationError({validation_error_message: 'filter syntax is incorrect'})

        return True
