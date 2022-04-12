from typing import Dict, List
from pymongo import MongoClient, database
from pymongo.cursor import Cursor
import certifi
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv()

USERNAME = os.environ.get("mongoUser")
PASSWORD = os.environ.get("mongoPass")
CONNECTION_STRING = os.environ.get("mongoURI")

CONNECTION_STRING = CONNECTION_STRING.replace("<user>", USERNAME)
CONNECTION_STRING = CONNECTION_STRING.replace("<password>", PASSWORD)

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
db: database.Database = client.get_default_database()


class MongoConnector:
    def getCollection(collection: str) -> Cursor:
        collection = db[collection]
        return collection.find()

    def addOne(collection: str, data: Dict) -> None:
        collection = db[collection]
        collection.insert_one(data)

    def addMany(collection: str, data: List[Dict]) -> None:
        collection = db[collection]
        collection.inser_many(data)

    def updateOne(collection: str, filter, data: Dict, upsert: bool) -> None:
        collection = db[collection]
        collection.replace_one(filter, data, upsert=upsert)
