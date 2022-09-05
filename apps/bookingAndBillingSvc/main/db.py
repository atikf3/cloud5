import os
import sys
import urllib.parse
from dotenv import load_dotenv

from bson.objectid import ObjectId
from flask import current_app as app
from flask_pymongo import PyMongo
# from flask.ext.sqlalchemy import SQLAlchemy # TODO
from pymongo import MongoClient

from core import utils


class MongoDB:
    def __init__(self):
        self.log = app.config["log"]
        self.utils = utils.Utils()
        load_dotenv("../.env")
        # self.config = self.utils.get_config()
        self.db_config()
        self.connect()

    def connect(self):
        self.mongo = PyMongo(app)

    def db_config(self):
        app.config["MONGO_DBNAME"] = os.environ.get("MONGODB_DATABASE")
        dbname = os.environ.get("MONGODB_DATABASE")
        app.config["HOST"] = os.environ.get("MONGODB_HOSTNAME")
        username = os.environ.get("MONGODB_USERNAME")
        # password = urllib.parse.quote_plus(os.environ.get("MONGODB_PASSWORD")) # enable if plain password
        password = os.environ.get("MONGODB_PASSWORD") # enable this if  pass has no special symbols
        host = app.config["HOST"]
        mongo_uri = f"mongodb://{username}:{password}@{host}:27017/{dbname}"
        app.logger.debug(f'Mongo URI: [{mongo_uri}]')
        app.config["MONGO_URI"] = mongo_uri
        client = MongoClient(mongo_uri)

        try:
            client.server_info()
            self.log.debug("Database connected successfully")
            self.client = client
        except Exception as e:
            self.log.error(
                f"MongoDB Connection Error check ./.env for details. Authstring: {mongo_uri} Error: {e}"
            )
            sys.exit(1)
        finally:
            client.close()

    def find(self, collection, condition=None):
        self.log.debug(f"Find {condition} from {collection} collection.")
        if condition:
            try:
                data = self.mongo.db[collection].find(condition)
            except Exception as e:
                self.log.error(f"{e}")
                data = f"No collection found with {collection}"
        else:
            data = self.mongo.db[collection].find()

        results = self.mongo_id_to_str(data)

        return results

    def find_by_id(self, collection, _id):
        results = None
        self.log.debug(f"Find by _id {_id} from {collection}")
        if _id:
            try:
                results = self.mongo.db[collection].find_one({"_id": ObjectId(_id)})
                results["_id"] = str(results["_id"])
            except Exception as e:
                self.log.error(f"Something went wrong. Error: {e}")
        else:
            results = self.mongo.db[collection].find()

        return results

    def save(self, collection, obj):
        """
        Takes data obj as input and returns the _id after saving
        """
        self.log.debug(f"Insert {obj} into {collection}")
        _id = self.mongo.db[collection].insert_one(obj).inserted_id
        result = self.find_by_id(collection, _id)

        if result:
            result["_id"] = str(result["_id"])

        return result

    def update(self, collection, _id, obj):
        """
        Updates the object based on _id
        Output: (error, message or obj)
        """
        obj = self.remove_empty_keys(obj)
        self.log.debug(f"Update {obj} into {collection} by {_id}")
        if _id:
            try:
                inserted_id = self.mongo.db[collection].update_one(
                    {"_id": ObjectId(_id)}, obj
                )
                result = (True, self.find_by_id(collection, _id))
            except Exception as e:
                self.log.error(f"ID is not valid. err: {e}")
                result = (False, f"{e}")

            return result
        else:
            return (False, "_id is required")

    def delete(self, collection, _id):
        self.log.debug(f"Delete from {collection} by {_id}")
        try:
            self.mongo.db[collection].delete_one({"_id": ObjectId(_id)})
            return (True, "Delete Successfully")
        except Exception as e:
            self.log.error(f"Document not deleted using {_id}. err: {e}")
            return (False, f"Error in Deleting document using {_id}")

    def remove_empty_keys(self, obj):
        """
        Input: Take an object with key, values
        Ouput: Returns the object by removing keys which has no values
        """
        new_obj = {}
        new_obj["$set"] = {k: v for k, v in obj["$set"].items() if v != ""}
        return new_obj

    def mongo_id_to_str(self, data):
        results = []
        if type(data) == str:
            return False

        for document in data:
            document["_id"] = str(document["_id"])
            results.append(document)

        return results

class MySQL:
    def __init__(self):               # Build the class consuctor
        self.log = app.config["log"]       
        self.utils = utils.Utils()         
        load_dotenv("../.env")
        self.db_con = self.connect()
        self.db_cur = self.db_con.cursor()                                       # Get a db cursor
        self.cur_offset = 0                                                      # This class var is used to track SQL OFFSET when
        self.cur_order_by = "address"                                            # Persit the current order value
        self.cur_limit_by = 6

    def execute_query(self, query_string):                                       # Methdd used to execute SQL INSER, UPDATA and DELETE
      self.db_cur.execute(query_string)                                          # Uses pymsql execute
      self.db_con.commit()                                                       # commit CRUD actions

    def execute_list(self,query_string):                                          # Called with Select * and query offset parm
       self.db_cur.execute(query_string)                                          # Execute the Select *

       rows = self.db_cur.fetchall()                                              # Fetching all records here to a varible
       return rows     

    def db_config(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['MYSQL_DB_URL'] + os.environ['MYSQL_APP_NAME']
        app.logger.debug(f'MySQL URI: [{app.config["SQLALCHEMY_DATABASE_URI"]}]')
        # client = MongoClient(mongo_uri)

        try:
            # try connection to mysql
            self.db = SQLAlchemy(app)
            self.log.debug(f"Connected to MySQL")
            self.client = self.db
        except Exception as e:
            self.log.error(f"Error in connecting to MySQL. Error: {e}")
            sys.exit(1)
        # finally:
        #     client.close()

    def find(self, db, condition=None):
        self.log.debug(f"Find {condition} from {db} database.")
        if condition:
            try:
                data = self.db.from_sql(f"SELECT * FROM {db} WHERE {condition}")
                # data = self.mongo.db[collection].find(condition)
            except Exception as e:
                self.log.error(f"{e}")
                data = f"No collection found with {db}"
        else:
            data = self.db.from_sql(f"SELECT * FROM {db}")
            # data = self.mongo.db[collection].find()

        results = self.sql_id_to_str(data)

        return results

    def connect(self):
        self.db = SQLAlchemy(app)
        # self.db_con = pymysql.connect('localhost', 'root', ' ', 'Homes')       # Basic connection string

    def find_by_id(self, db, _id):
        results = None
        self.log.debug(f"Find by _id {_id} from {db}")
        if _id:
            try:
                # results = self.mongo.db[collection].find_one({"_id": ObjectId(_id)})
                results = self.db.from_sql(f"SELECT * FROM {db} WHERE _id = {_id}")
                results["_id"] = str(results["_id"])
            except Exception as e:
                self.log.error(f"Something went wrong. Error: {e}")
        else:
            results = self.db.from_sql(f"SELECT * FROM {db}")
            # results = self.mongo.db[collection].find()

        return results

    def save(self, collection, obj):
        """
        Takes data obj as input and returns the _id after saving
        """
        self.log.debug(f"Insert {obj} into {collection}")
        # _id = self.mongo.db[collection].insert_one(obj).inserted_id
        _id = self.db.insert(collection, obj)
        result = self.find_by_id(collection, _id)

        if result:
            result["_id"] = str(result["_id"])

        return result

    def update(self, db, _id, obj):
        """
        Updates the object based on _id
        Output: (error, message or obj)
        """
        obj = self.remove_empty_keys(obj)
        self.log.debug(f"Update {obj} into {db} by {_id}")
        if _id:
            try:
                # self.db.update(db, {"_id": ObjectId(_id)}, obj)
                # update with sqlalchemy

                # inserted_id = self.mongo.db[collection].update_one(
                #     {"_id": ObjectId(_id)}, obj
                # )
                result = (True, self.find_by_id(db, _id))
            except Exception as e:
                self.log.error(f"ID is not valid. err: {e}")
                result = (False, f"{e}")

            return result
        else:
            return (False, "_id is required")

    def delete(self, db, _id):
        self.log.debug(f"Delete from {db} by {_id}")
        try:
            # self.mongo.db[collection].delete_one({"_id": ObjectId(_id)})
            self.db.delete(db, _id)
            return (True, "Delete Successfully")
        except Exception as e:
            self.log.error(f"Document not deleted using {_id}. err: {e}")
            return (False, f"Error in Deleting document using {_id}")

    def remove_empty_keys(self, obj):
        """
        Input: Take an object with key, values
        Ouput: Returns the object by removing keys which has no values
        """
        new_obj = {}
        new_obj["$set"] = {k: v for k, v in obj["$set"].items() if v != ""}
        return new_obj

    def sql_id_to_str(self, data):
        results = []
        if type(data) == str:
            return False

        for document in data:
            document["_id"] = str(document["_id"])
            results.append(document)

        return results