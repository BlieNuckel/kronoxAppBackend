from typing import Dict, List
from pymongo import MongoClient
from pymongo.cursor import Cursor
import certifi
import os

USERNAME = os.environ["mongoUser"]
PASSWORD = os.environ["mongoPass"]
CONNECTION_STRING = os.environ["mongoURI"]

CONNECTION_STRING = CONNECTION_STRING.replace("<user>", USERNAME)
CONNECTION_STRING = CONNECTION_STRING.replace("<password>", PASSWORD)

client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())


class MongoConnector:
    db = client["schedules"]

    def getCollection(self, collection: str) -> Cursor:
        collection = self.db[collection]
        return collection.find()

    def addOne(self, collection: str, data: Dict) -> None:
        collection = self.db[collection]
        collection.insert_one(data)

    def addMany(self, collection: str, data: List[Dict]) -> None:
        collection = self.db[collection]
        collection.inser_many(data)
