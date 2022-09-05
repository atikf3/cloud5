import json
import os
from flask import Flask
import pathlib
from flask_restx import Api

from main.apis.booking import api as Booking
from main.apis.billing import api as Billing
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

api = Api(app, authorizations=authorizations, version='1.0', title='Booking service - API docs',
    description='Booking service - CLO5 API.',
    doc='/docs',
    errors=Flask.errorhandler
)

# Endpoints
api.add_namespace(Booking, path='/v1')
api.add_namespace(Billing, path='/v1')

# Run Server
if __name__ == '__main__':
    app.run(use_reloader=True, host='0.0.0.0', port=os.getenv('APP_PORT',5053))
