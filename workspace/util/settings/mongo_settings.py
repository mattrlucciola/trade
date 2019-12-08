from db_params import db
def mongo_coll_cursor(collection_name, db_name = db['name']):
    import pymongo
    db_cursor = pymongo.MongoClient("mongodb://127.0.0.1:27018/")
    db_with_collection = db_cursor[db_name][collection_name]
    return db_with_collection
