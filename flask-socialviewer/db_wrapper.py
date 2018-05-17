# Starting the database:
# "C:\Program Files\MongoDB\Server\3.0\bin\mongod.exe" --dbpath C:\Users\tv\Projects\Personal\GitHub\socialmedia\db
import pymongo


# Exports Twitter data collected by TwitterThread threads to MongoDB
class SocialMediaMongoWrapper:

    # TwitterExportMongo Constructor
    # @param host MongoDB host string
    # @param port MongoDB port (default: 27017)
    # @param location Dictionary for the location.  Expe
    def __init__(self, host, location, socialmedia="twitter", port=27017):

        # @var host
        # MongoDB host string
        self.host = host

        # @var port
        # MongoDB port
        self.port = port

        # @var db_client
        # MongoDB Client Instance
        self.db_client = pymongo.MongoClient(host, port)

        # @var db
        # MongoDB Collection instance
        self.db = self.db_client[location['name']][socialmedia]

        # Write out location information so its available
        self.location_db = self.db_client[location['name']]['location']
        if self.location_db.find_one({"name": location["name"]}) is None:
            self.location_db.insert_one(location)
        else:
            self.location_db.update_one({"name": location["name"]}, {"$set": location}, upsert=False)

    # Writes a data item to MongoDB
    # @param data Data dictionary
    # @return No return value.
    def add_data(self, data):
        if type(data) is list and len(data) > 0:
            self.db.insert_one (data)
        elif type(data) is dict:
            self.db.insert_one (data)

    def get_location(self):
        return self.location_db.find_one({})

    def get_data(self):
        return self.db.find({})

    # Shuts down open file handles
    # @return No return value.
    def shutdown(self):
        self.db_client.close()


def get_mongodb_list(host='localhost', location=None, port=27017):
    mongo_client = pymongo.MongoClient(host, port)
    if location:
        media_list = list(mongo_client[location].collection_names())
        media_list.remove("local")
        return media_list

    db_list = list(mongo_client.database_names())
    db_list.remove("local")

    mongo_client.close()
    return db_list


def get_location(location_str, host='localhost', port=27017):
    mongo_client = pymongo.MongoClient(host, port)
    location_db = mongo_client[location_str]['location']

    mongo_client.close()
    return location_db.find_one({})


def get_location_count(location_str, socialmedia, host='localhost', port=27017):
    db_client = pymongo.MongoClient(host, port)
    db = db_client[location_str][socialmedia]

    count = len([x for x in db.find({})])
    print(db.find({}))
    print(location_str, socialmedia, count)
    db_client.close()
    return count

