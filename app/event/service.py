import requests

from typing import List, Dict

from app.database import get_default_strategy_collection, get_destinations_collection

from .exceptions import CustomFilterExecutionException, RoutesNotFound

request_map = {
    'get': requests.get,
    'post': requests.post,
    'put': requests.put
}


def get_strategy(received_data: Dict) -> tuple[str, bool]:
    """
    Get strategy passed by user. If no strategy is passed get default strategy from database. If strategy is passed
    by user default strategy in database will be replaced by new strategy.
    :param received_data: data from received request
    :return: returns received or default strategy and flag variable that signals whether to overwrite default strategy
             in database or not
    """
    strategy = received_data.get('strategy')
    need_to_rewrite = True

    if not strategy:
        strategy = list(get_default_strategy_collection().find({}, {'_id': 0, 'strategy': 1}))[0].get('strategy')
        need_to_rewrite = False

    return strategy, need_to_rewrite


def update_strategy(new_strategy: str):
    """
    Update strategy document replacing old strategy with passed one
    :param new_strategy: new strategy that will replace old one in database
    :return: None
    """
    get_default_strategy_collection().find_one_and_update({}, {"$set": {'strategy': new_strategy}})


def get_destinations_from_database() -> Dict:
    """
    Receives list of stored destinations from database. Convert list to dict, that contain data
    in format {destination_name: destination data} and returns it
    :return: dictionary of destinations from database
    """
    destinations_from_database = list(get_destinations_collection().find({}, {'_id': 0}))
    destinations = {destination.pop('destinationName'): destination for destination in destinations_from_database}

    return destinations


def execute_custom_strategy(custom_strategy: str, routes: List) -> List:
    """
    Execute code and filters passed routingIntents
    :param custom_strategy: filter written by user
    :param routes: routingIntents that will be filtered
    :return: returns filtered routes
    """
    strategy_code = f'({custom_strategy})({routes})'
    try:
        filtered_destinations = [route.get('destinationName') for route in eval(strategy_code)]
        return filtered_destinations
    except Exception as e:
        raise CustomFilterExecutionException({'custom_filter_execution_error': e.args[0]})


def filter_destinations_by_strategy(routes: List, strategy: str) -> List:
    """
    Filter routes according to passed strategy
    :param routes: passed routingIntents
    :param strategy: strategy which be used to filter routes
    :return: returns list of filtered routes
    """

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
    """
    Sends payload to received destination using according transport
    :param destination: contain destination data
    :param destination_name: destination name that will be used to print result
    :param payload: payload that will be sent to destination
    :return: returns True if payload was sent successfully
    """
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


def check_if_destination_valid(destination: str, destinations_in_database: Dict, filtered_destinations: List) -> bool:
    """
    Checks if destination valid. Destination valid if it in filtered destinations and in database.
    :param destination: destination name that will be used to look
    :param destinations_in_database: dictionary of destinations from database
    :param filtered_destinations: list of filtered destinations
    :return: returns result of check
    """
    destination_is_valid = True

    if destination not in destinations_in_database:
        print(f'UnknownDestinationError {destination}')
        destination_is_valid = False

    elif destination not in filtered_destinations:
        print(f'{destination} skipped')
        destination_is_valid = False

    return destination_is_valid


def route_event(payload: Dict, routing_intents: List, strategy: str) -> Dict:
    """
    Routes event to destination from routing_intents that passed filtration according to strategy
    :param payload: payload that will be sent
    :param routing_intents: list of destinations user wants to send payload to
    :param strategy: strategy for filtrating destinations
    :return: returns a list of the results of routing the event to the passed destinations
    """
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

