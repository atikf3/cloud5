import datetime
import logging as log
import os

import coloredlogs
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import ( JWTManager )
import pathlib

# local imports
from config import app_config
from .db import MongoDB

def create_app(config_name):
    config_name = "dev" if not config_name else config_name
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    # app.config.from_pyfile("config.py")
    
    logLevel = log.getLevelName(os.environ.get('APP_LOG_LEVEL', 'INFO'))
    log.basicConfig(
        level=logLevel,
        # format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
        format=f'%(asctime)s %(levelname)s: %(message)s'
    )
    coloredlogs.install(
        level=logLevel,
        logger=app.logger,
        # fmt=f'%(asctime)s %(levelname)s [%(module)s] [%(pathname)s:%(lineno)d]: %(message)s'
        fmt=f'%(asctime)s %(levelname)s [%(module)s]: %(message)s'
        )
    app.config["log"] = log
    # app.logger.addHandler(log.StreamHandler())
    # app.logger.setFormat(f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    app.logger.debug(f'logginglevel: {app.logger.getEffectiveLevel()}')

    cors = CORS(app, supports_credentials=True,  resources={r"/*": {"origins": "*"}})
    # app.config["CORS_HEADERS"] = "Content-Type"
    app.config['DEBUG'] = os.environ.get('APP_DEBUG', False)

    # app.debug_log_format = "%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s"
    app.config["JWT_SECRET_KEY"] = os.environ.get('APP_SECRET_KEY', "__change__me__mls__secret_key__")
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=10)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config["jwt"] = JWTManager(app)
    app.config["flask_bcrypt"] = Bcrypt(app)
    jwt = app.config["jwt"]


    #MAIL
    app.config['ROOT_DIR'] = pathlib.Path(__file__).parent.absolute()

    app.config['MAIL_SERVER']='smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = '5f66e597d81029'
    app.config['MAIL_PASSWORD'] = 'a507bcdb26ce8e'
    app.config['MAIL_USERNAME'] = '2320c8190e54ae'
    app.config['MAIL_PASSWORD'] = '5e40ff1df38cc8'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEBUG'] = True
    # Swagger UI config
    app.config.SWAGGER_UI_JSONEDITOR = True
    app.config.SWAGGER_UI_DOC_EXPANSION = "list"  # none, list, full

    with app.app_context():
        db = MongoDB()

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        blacklist = set()
        jti = jwt_payload["jti"]
        return jti in blacklist
        # jti = jwt_payload["jti"]
        # # token = db.find('blacklist',  {'token': jti})
        # token =  db.blacklist.count_documents({'token': jti}, limit = 1)
        # # return self.mongo.save('tokenBlocklist', {'blockedToken': jti})
        # # return token is not None
        # return token is not None and token > 0

    @app.route("/")
    def hello_world():
        # render home template
        app.logger.debug("homepageeeeee")
        return "Hello world from <b>Catalog</b> API. Documentation at <a href='/docs'>/docs</a>."

    return app



class UserService:
    """ doc string for UserService """

    def __init__(self):
        super(UserService, self).__init__()
        self.collection = "users"
        self.blacklist = BlacklistHelper()
        self.utils = Utils()
        self.mongo = MongoDB()

    def user_list(self):
        users = self.mongo.find(self.collection)
        if users:
            for user in users:
                del user["password"]
            return users
        else:
            return []

    def add_user(self, user_obj):
        """ user_obj - user object """
        user = self.mongo.find(self.collection, {"email": user_obj["email"]})
        if not user:
            return self.mongo.save(self.collection, user_obj)
        else:
            return f'User with {user_obj["email"]} already exists.'