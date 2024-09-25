import pytest

from app.event.exceptions import CustomFilterExecutionException
from app.event.service import get_strategy, update_strategy, get_destinations_from_database, execute_custom_strategy, \
    filter_destinations_by_strategy, send_payload, check_if_destination_valid, route_event


USER_REQUEST_BODY = {
    "payload": {"a": "1"},
    "routingIntents": [
        {
            "destinationName": "destination1",
            "important": True,
            "bytes": 15,
            "score": 0
        },
        {
            "destinationName": "destination2",
            "important": False
        },
        {
            "destinationName": "destination3",
            "bytes": 15,
            "score": 1
        },
        {
            "destinationName": "destination43",
            "bytes": 15,
            "score": 0
        }
    ],
    "strategy": "small"
}


async def test_get_strategy_with_strategy_in_request(app, default_strategy):
    received_strategy, need_to_rewrite = get_strategy(USER_REQUEST_BODY)
    assert received_strategy
    assert received_strategy == USER_REQUEST_BODY.get('strategy')
    assert need_to_rewrite


async def test_get_strategy_without_strategy_in_request(app, default_strategy):
    request = USER_REQUEST_BODY.copy()
    request.pop('strategy')
    received_strategy, need_to_rewrite = get_strategy(request)
    assert received_strategy
    assert received_strategy == default_strategy.get('strategy')
    assert not need_to_rewrite


async def test_update_strategy(app, default_strategy):
    update_strategy('important')

    request = USER_REQUEST_BODY.copy()
    request.pop('strategy')

    received_strategy, need_to_rewrite = get_strategy(request)

    assert received_strategy != default_strategy.get('strategy')
    assert received_strategy == 'important'


async def test_get_destinations_from_database(app, destinations):
    destination_names = [i.get('destinationName') for i in USER_REQUEST_BODY.get('routingIntents')]
    received_destinations = get_destinations_from_database(destination_names)
    assert received_destinations


async def test_execute_custom_filter_strategy():
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = "lambda routes: [i for i in routes if i.get('score') == 1]"
    filtered_routes = execute_custom_strategy(strategy, routes)

    assert filtered_routes
    assert 'destination3' in filtered_routes


async def test_error_when_executing_custom_filter_strategy():
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = "lambda routes: [i for i in routes if i.get('score' == 1]"

    with pytest.raises(CustomFilterExecutionException):
        execute_custom_strategy(strategy, routes)


async def test_filter_destinations_by_all_strategy():
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = 'all'
    filtered_destinations = filter_destinations_by_strategy(routes, strategy)

    assert filtered_destinations


async def test_filter_destinations_by_small_strategy():
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = 'small'
    filtered_destinations = filter_destinations_by_strategy(routes, strategy)

    assert filtered_destinations
    assert 'destination2' not in filtered_destinations
    assert 'destination1' in filtered_destinations


async def test_filter_destinations_by_important_strategy():
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = 'important'
    filtered_destinations = filter_destinations_by_strategy(routes, strategy)

    assert filtered_destinations
    assert 'destination2' not in filtered_destinations
    assert 'destination1' in filtered_destinations


async def test_filter_destinations_by_custom_strategy():
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = "lambda routes: [i for i in routes if i.get('score') == 1]"
    filtered_destinations = filter_destinations_by_strategy(routes, strategy)

    assert filtered_destinations
    assert 'destination2' not in filtered_destinations
    assert 'destination3' in filtered_destinations


async def test_send_payload():
    destination = {'destinationName': "destination1", 'transport': "log.warn"}
    destination_name = 'destination1'
    payload = USER_REQUEST_BODY.get('payload')

    result = send_payload(destination, destination_name, payload)

    assert result


async def test_send_payload_to_http():
    destination = {'destinationName': "destination1", 'transport': "http.get", 'url': "http://example.com"}
    destination_name = 'destination1'
    payload = USER_REQUEST_BODY.get('payload')

    result = send_payload(destination, destination_name, payload)

    assert result


async def test_check_if_destination_is_valid():
    destination = 'destination1'
    destinations_in_db = {'destination1': {}, 'destination2': {}}
    filtered_destinations = ['destination1', 'destination3']
    result = check_if_destination_valid(destination, destinations_in_db, filtered_destinations)

    assert result


async def test_check_destination_not_filtered():
    destination = 'destination2'
    destinations_in_db = {'destination1': {}, 'destination2': {}}
    filtered_destinations = ['destination1', 'destination3']
    result = check_if_destination_valid(destination, destinations_in_db, filtered_destinations)

    assert not result


async def test_check_destination_unknown():
    destination = 'destination5'
    destinations_in_db = {'destination1': {}, 'destination2': {}}
    filtered_destinations = ['destination1', 'destination3']
    result = check_if_destination_valid(destination, destinations_in_db, filtered_destinations)

    assert not result


async def test_route_event(app, destinations):
    payload = USER_REQUEST_BODY.get('payload')
    routes = USER_REQUEST_BODY.get('routingIntents')
    strategy = 'all'
    result = route_event(payload, routes, strategy)

    assert result
    assert result.get('destination1') is True
    assert result.get('destination43') is False
