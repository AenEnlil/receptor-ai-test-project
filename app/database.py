from pymongo import MongoClient

from .config import get_settings

mongo_client = MongoClient(get_settings().MONGO_URL)
db = mongo_client[get_settings().DATABASE_NAME]

LOGS_DOC = 'logs'
DEFAULT_STRATEGY_DOC = 'default_strategy'
DESTINATIONS_DOC = 'destinations'


def get_logs_collection():
    return db.get_collection(LOGS_DOC)


def get_default_strategy_collection():
    return db.get_collection(DEFAULT_STRATEGY_DOC)


def get_destinations_collection():
    return db.get_collection(DESTINATIONS_DOC)
