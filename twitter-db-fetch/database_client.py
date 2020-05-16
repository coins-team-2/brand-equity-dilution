from pymongo import MongoClient
import pymongo
import config


class DatabaseClient:
    def __init__(self):
        db_connection_string = config.secrets["db-connection-string"]
        self.client = MongoClient(db_connection_string)
        self.database = self.client["coins-brand-equity-dilution-database"]

    def getLatestTweetId(self, collection_name):
        tweets = list(self.database[collection_name].find())

        if len(tweets) == 0:
            return -1

        max_id = max(list(map(lambda tweet: int(tweet['id_str']), tweets)))
        print("Most recent tweet in " + collection_name +
              " collection has id " + str(max_id) + ".")
        return max_id

    def getAllDocuments(self, collection_name):
        return list(self.database[collection_name].find())

    def saveDocuments(self, collection_name, documents):
        self.database[collection_name].insert_many(documents)
        print('Successfully saved ' + str(len(documents)) +
              ' documents to database ' + collection_name + '.')