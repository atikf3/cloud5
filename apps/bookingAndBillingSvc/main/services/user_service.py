from flask import current_app as app

from core.utils import Utils
from main.db import MongoDB
from main.services.blacklist_helpers import BlacklistHelper

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
    
    def find_user_by_id(self, user_id):
        user = self.mongo.find_by_id(self.collection, user_id)
        if user:
            if user["status"] != "enabled" and user["role"] != "admin":
                app.logger.info('AFKJHDKJHGKJHG')
                return ("error", [], "Account is disabled and not admin.", 400)
            del user["password"]
            return ("success", user, "ok", 200)
        else:
            return ("error", [], "Something went wrong.", 400)

    def add_user(self, user_obj):
        """ user_obj - user object """
        user = self.mongo.find(self.collection, {"email": user_obj["email"]})
        if not user:
            user_obj['role'] = 'user'
            user_obj['status'] = 'enabled'
            return self.mongo.save(self.collection, user_obj)
        else:
            return f'User with {user_obj["email"]} already exists.'


    def add_user_admin(self, user_obj, current_user_id):
        """ user_obj - user object """
        current_user = self.mongo.find_by_id(self.collection, current_user_id)
        if not current_user:
            return ("error", [], "Toekn expired, please relogin.", 401)
        if current_user["role"] != "admin":
            return ("error", [], "You are not allowed to create users.", 401)
        return self.add_user(user_obj)

    def get_user_by_id(self, user_id):
        """ Get User profile by id. ex _id:  """
        res = self.mongo.find_by_id(self.collection, user_id)
        if res:
            del res["password"]
            return ("success", res, "ok", 200)
        else:
            return ("error", [], "Something went wrong.", 400)

    def get_user_by_mail(self, user_mail):
        """ Get User profile by mail. ex mail:  """
        res = self.mongo.find(self.collection, {"email": user_mail})
        if res:
            if res[0]:
                res = res[0]
                if 'password' in res:
                    del res["password"]
            return {'data': res, 'status': "ok" }
        else:
            return {'data': {}, 'status': "error" }

    def update_user(self, _id, user_obj, current_user_id):
        # log current user_id
        app.logger.info(f"Current user is {current_user_id}")
        current_user = self.mongo.find_by_id(self.collection, current_user_id)
        if not current_user:
            return ("error", [], "Toekn expired, please relogin.", 401)
        user = self.mongo.find(self.collection, {"_id": _id})
        if not user:
            # if user is not an admin or id is not the same as the current_user, deny
            app.logger.info(f"User {current_user_id} is trying to update user {_id}")
            # log user role and id
            app.logger.info(f"User role is {current_user['role']}")
            # log user id and _id
            app.logger.info(f"User id is {current_user['_id']} and _id is {_id}")
            if current_user["role"] != "admin" and current_user["_id"] != _id:
                return ("error", [], "You are not allowed to update this user.", 401)
            query = {"$set": user_obj}
            res, res_obj = self.mongo.update(self.collection, _id, query)
            if res:
                del res_obj["password"]
                # if res_obj["type"] == "seller" and res_obj["status"] == "disabled":
                #     app.logger.info(f'Seller {_id} is disabled, deleting products')
                #     self.product_service.disable_products_by_userid(_id)
                return ("success", res_obj, "ok", 200)
            else:
                return ("error", "", "Something went wrong.", 400)
        else:
            return (
                "error",
                "",
                f'Email {user_obj["email"]} is already in use!',
                400,
            )

    def delete_user(self, user_id):
        return self.mongo.delete(self.collection, user_id)

    def login(self, email):
        """ email as input """
        user = self.mongo.find(self.collection, {"email": email})
        if user:
            user = user[0]
            return user
        else:
            return None

    def save_tokens(self, user_tokens, claims=None, additional_claims={}):
        if claims is None:
            claims = app.config["JWT_IDENTITY_CLAIM"]
        app.logger.info(f"Saving tokens for claim {claims}")
        for token in user_tokens:
            app.logger.info(f'Adding token {user_tokens[token]}')
            self.blacklist.add_token_to_database(user_tokens[token], claims, additional_claims)
        # self.blacklist.add_token_to_database(
        #     user_tokens["access"], claims
        # )
        # self.blacklist.add_token_to_database(
        #     user_tokens["refresh"], claims
        # )
