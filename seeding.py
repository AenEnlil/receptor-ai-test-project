from pymongo.errors import BulkWriteError

from app.database import DESTINATIONS_DOC, DEFAULT_STRATEGY_DOC, db

initial_data = {
    DESTINATIONS_DOC: [
        {
            'destinationName': 'destination1',
            'transport': 'http.get',
            'url': 'http://example.com'
         },
        {
            'destinationName': 'destination2',
            'transport': 'http.post',
            'url': 'http://example.com'
        },
        {
            'destinationName': 'destination3',
            'transport': 'log.info',
        },
        {
            'destinationName': 'destination4',
            'transport': 'log.warn',
        }
    ],
    DEFAULT_STRATEGY_DOC: {'strategy': 'all'}
}


def remove_duplicates(data_list, looking_field, duplicates) -> list:
    return [i for i in data_list if i[looking_field] not in duplicates]


def clear_destinations_collection_data(collection_name):
    looking_field = 'destinationName'
    data = initial_data.get(collection_name).copy()
    destinations = [item.get(looking_field) for item in data]

    query = db.get_collection(collection_name).find({looking_field: {'$in': destinations}},
                                                    {looking_field: 1, '_id': 0})
    founded_destinations = [value[looking_field] for value in list(query)]
    cleared_data = remove_duplicates(data, looking_field, founded_destinations)
    return cleared_data


def clear_strategy_collection_data(collection_name):
    looking_field = 'strategy'
    data = initial_data.get(collection_name).copy()
    strategy = data.get(looking_field)
    query = db.get_collection(collection_name).find({looking_field: strategy},
                                                    {looking_field: 1, '_id': 0})
    founded_strategy = [value[looking_field] for value in list(query)]
    cleared_data = remove_duplicates([data], looking_field, founded_strategy)
    return cleared_data


def clear_collection_data(collection_name) -> list:
    match collection_name:
        case 'destinations':
            return clear_destinations_collection_data(collection_name)
        case 'default_strategy':
            return clear_strategy_collection_data(collection_name)


def init_database() -> None:
    collections = initial_data.keys()

    for collection_name in collections:
        collection = db.get_collection(collection_name)
        cleared_data = clear_collection_data(collection_name)

        if cleared_data:
            try:
                collection.insert_many(cleared_data)
            except BulkWriteError:
                continue


if __name__ == "__main__":
    init_database()
