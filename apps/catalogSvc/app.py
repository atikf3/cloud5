import json
import os
from flask import Flask
import pathlib
from flask_restx import Api

from main.apis.hotel import api as Hotel
from main.apis.room import api as Room
from main.db import MongoDB

from main import create_app

authorizations = {
    'token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description' : 'Put "Bearer theToken" in here.'
    }
}

config_name = os.getenv('APP_ENV')
app = create_app(config_name)

api = Api(app, authorizations=authorizations, version='1.0', title='Catalog Service API docs',
    description='Catalog Service - CLO5 API.',
    doc='/docs',
    errors=Flask.errorhandler
)

def preload_db():
    with open('./dbinit.json', 'r') as f:
        dbstuff = json.load(f)

    db = MongoDB()

    for entity in dbstuff:
        if entity == 'users':
            # if 'users' not in db.mongo.db.list_collection_names():
            #     db.mongo.createCollection('users')
            for user in dbstuff[entity]:
                app.logger.info(f'Inserting user {user["email"]}')
                # app.logger.info('countDocs', db.mongo.db['users'].count_documents({}) or 'bob')
                # app.logger.info('findUser', db.find('users', {'email': user['email']}) or 'bob')
                if db.mongo.db['users'].count_documents({}) != 0 and db.find('users', {'email': user['email']}):
                    continue
                else:
                    user.update((k, app.config["flask_bcrypt"].generate_password_hash(v)) for k, v in user.items() if k == "password")
                    db.save('users', user)
        else:
            if db.mongo.db[entity].count_documents({}) != 0: #and db.find(entity, {'email': user['email']}):
                app.logger.info(f'{entity} already exists and is populated or does not exists., skipping.')
                continue
            else:
                app.logger.info(f'working on {entity}')
                for data in dbstuff[entity]:
                    # if data has key hotel_id 
                    if 'hotel_id' in data and data['hotel_id']:
                        app.logger.info(f'Finding {entity} {data["hotel_id"]} UID')
                        ouid = db.find('hotels', {'hotel_name': data['hotel_id']}) or None
                        if not ouid:
                            continue
                        data['hotel_id'] = ouid[0]['_id'] or None
                    app.logger.info(f'Inserting {entity} {data}')
                    db.save(entity, data)

@app.before_first_request
def insert_stuff():
    # if env variable 'APP_PRELOAD_DB' is set to 'true', then insert data into db
    if os.getenv('APP_PRELOAD_DB') == 'true':
        preload_db()

# Endpoints
api.add_namespace(Hotel, path='/v1')
api.add_namespace(Room, path='/v1')

# Run Server
if __name__ == '__main__':
    app.run(use_reloader=True, host='0.0.0.0', port=os.getenv('APP_PORT',5052))
