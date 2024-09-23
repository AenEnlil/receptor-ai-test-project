from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from app.auth.dependencies import JWTBearer
from app.event.schemas import EventInputSchema
from .service import get_strategy, route_event, update_strategy

router = APIRouter(
    prefix='/event',
    tags=['event']
)


@router.post('/handle-event', dependencies=[Depends(JWTBearer())])
async def handle_event(event: EventInputSchema):
    data = event.model_dump(exclude_unset=True)
    payload = data.get('payload')
    routing_intents = data.get('routingIntents')
    strategy, need_to_rewrite = get_strategy(data)
    try:
        result = route_event(payload, routing_intents, strategy)
        if need_to_rewrite:
            update_strategy(strategy)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e.args[0])
