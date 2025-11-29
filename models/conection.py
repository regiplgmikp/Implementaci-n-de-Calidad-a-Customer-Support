from pymongo import MongoClient 

def connect_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['customer_support']
    return db

