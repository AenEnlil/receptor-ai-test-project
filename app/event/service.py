from enum import Enum
from typing import List, Dict
import requests


from app.database import get_default_strategy_collection, get_destinations_collection
from .exceptions import CustomFilterExecutionException, RoutesNotFound

request_map = {
    'get': requests.get,
    'post': requests.post,
    'put': requests.put
}


def get_strategy(received_data: Dict):
    strategy = received_data.get('strategy')
    need_to_rewrite = True

    if not strategy:
        strategy = list(get_default_strategy_collection().find({}, {'_id': 0, 'strategy': 1}))[0].get('strategy')
        need_to_rewrite = False

    return strategy, need_to_rewrite


def update_strategy(new_strategy: str):
    get_default_strategy_collection().find_one_and_update({}, {"$set": {'strategy': new_strategy}})


def get_destinations_from_database():
    destinations_from_database = list(get_destinations_collection().find({}, {'_id': 0}))
    destinations = {destination.pop('destinationName'): destination for destination in destinations_from_database}

    return destinations


def execute_custom_strategy(custom_strategy, routes):
    strategy_code = f'({custom_strategy})({routes})'
    try:
        filtered_destinations = [route.get('destinationName') for route in eval(strategy_code)]
        return filtered_destinations
    except Exception as e:
        raise CustomFilterExecutionException({'custom_filter_execution_error': e.args[0]})


def filter_destinations_by_strategy(routes: List, strategy: str):

    match strategy:
        case 'all':
            filtered_destinations = [route.get('destinationName') for route in routes]
        case 'important':
            filtered_destinations = [route.get('destinationName') for route in routes if route.get('important')]
        case 'small':
            filtered_destinations = [route.get('destinationName') for route in routes if route.get('bytes') and
                                     route.get('bytes') < 1024]
        case _:
            filtered_destinations = execute_custom_strategy(strategy, routes)
    return filtered_destinations


def send_payload(destination: Dict, destination_name: str, payload: Dict) -> bool:
    transport = destination.get('transport')
    protocol, method = transport.split('.')

    try:
        if protocol == 'http':
            send_function = request_map.get(method)
            send_function(url=destination.get('url'), data=payload)

        print(f"payload sent to [{destination_name}] via [{transport}] transport")
        return True

    except Exception:
        return False


def check_if_destination_valid(destination, destinations_in_database, filtered_destinations):
    destination_is_valid = True

    if destination not in destinations_in_database:
        print(f'UnknownDestinationError {destination}')
        destination_is_valid = False

    elif destination not in filtered_destinations:
        print(f'{destination} skipped')
        destination_is_valid = False

    return destination_is_valid


def route_event(payload: Dict, routing_intents: List, strategy: str) -> Dict:
    result = {}
    filtered_destinations = filter_destinations_by_strategy(routing_intents, strategy)
    if not filtered_destinations:
        raise RoutesNotFound('No routes found with current strategy')

    destinations_in_database = get_destinations_from_database()

    for route in routing_intents:
        route_destination = route.get('destinationName')

        if not check_if_destination_valid(route_destination, destinations_in_database, filtered_destinations):
            result.update({route_destination: False})
            continue

        destination_data = destinations_in_database.get(route_destination)
        send_result = send_payload(destination_data, route_destination, payload)
        result.update({route_destination: send_result})

    return result

