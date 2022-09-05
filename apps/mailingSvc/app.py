import json
import os
from flask import Flask
import pathlib
from flask_restx import Api

from main.apis.mailer import api as Mailer
from main.db import MongoDB

from main import create_app

from flask_mail import Mail

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

# TODO: @abdelhanine: Fix this, makes whole API crash
mail = Mail(app)

api = Api(app, authorizations=authorizations, version='1.0', title='Mailing service - API docs',
    description='Mailing service - CLO5 API.',
    doc='/docs',
    errors=Flask.errorhandler
)

# Endpoints
api.add_namespace(Mailer, path='/v1')

# Run Server
if __name__ == '__main__':
    app.run(use_reloader=True, host='0.0.0.0', port=os.getenv('APP_PORT',5054))
