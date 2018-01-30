import pymongo


class Datebase(object):
    Uri = "mongodb://127.0.0.1:27017"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Datebase.Uri)
        Datebase.DATABASE = client['my-website']

    @staticmethod
    def insert(collection, data):
        Datebase.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Datebase.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Datebase.DATABASE[collection].find_one(query)

    @staticmethod
    def remove(collection, query):
        return Datebase.DATABASE[collection].remove(query)

    @staticmethod
    def edit(collection, query, data):
        return Datebase.DATABASE[collection].update_one(query, {"$set": data})
