from fastapi import APIRouter

from app.event.schemas import EventInputSchema
from .service import get_strategy, route_event, update_strategy

router = APIRouter(
    prefix='/event',
    tags=['event']
)


@router.post('/handle-event')
async def handle_event(event: EventInputSchema):
    data = event.model_dump(exclude_unset=True)
    payload = data.get('payload')
    routing_intents = data.get('routingIntents')
    strategy, need_to_rewrite = get_strategy(data)

    result = route_event(payload, routing_intents, strategy)

    if need_to_rewrite:
        update_strategy(strategy)

    return result
