from pymongo import MongoClient

from .config import get_settings

mongo_client = MongoClient(get_settings().MONGO_URL)
db = mongo_client[get_settings().DATABASE_NAME]

