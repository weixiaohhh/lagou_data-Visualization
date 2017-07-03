from pymongo import MongoClient
import random
import json


class MongodbClient(object):

    def __init__(self, name, host, port):
        self.name = name
        self.client = MongoClient(host, port)
        self.db = self.client.lg

    def find(self,dict=None):
        return self.db[self.name].find(dict)
    
        
    def changeTable(self, name):
        self.name = name


    def put(self, dict):

        self.db[self.name].insert(dict)


    def delete(self, value):
        self.db[self.name].delete_one(value)    


    def getAll(self):
        return [p for p in self.db[self.name].find()]


    def clean(self):
        self.client.drop_database(self.name)


    def delete_all(self):
        self.db[self.name].remove()


if __name__ == "__main__":
    db = MongodbClient('first', 'localhost', 27017)
    db.put('127.0.0.1:1')
    db2 = MongodbClient('second', 'localhost', 27017)
    db2.put('127.0.0.1:2')
    db.clean()