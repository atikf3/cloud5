from flask_restx import Namespace, Resource, fields

api = Namespace("Authentication", description="Authentication related APIs")
from flask import request, current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    # jwt_refresh_token_required,
    jwt_required,
)
import json

from core.utils import Utils
from main.services.blacklist_helpers import BlacklistHelper
from main.services.jwt_service import JWTService
from main.services.user_service import UserService

register_model = {
    "name": fields.String(description="Name of the user", required=True, default='bob'),
    "email": fields.String(description="Email address", required=True, default='bob@c.lo'),
    "password": fields.String(description="password", required=True, default='Clo123$'),
    "type": fields.String(description="staff, customer", required=True, default='customer'),
}
user_register_model = api.model("SignupModel", register_model)


@api.route("/auth/register")
class UserRegister(Resource):
    """docstring for UserRegister."""

    def __init__(self, arg):
        super(UserRegister, self).__init__(arg)
        self.jwt_service = JWTService()
        self.blacklist = BlacklistHelper()
        self.utils = Utils()
        self.user_service = UserService()

    @api.expect(user_register_model)
    # @jwt_required()
    # @api.doc(security='token')
    def post(self):
        """ Register new User """
        api.logger.debug('A new user is trying to register')

        if not self.utils.checkEntityKeysInRequest(register_model, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        request.json["password"] = self.jwt_service.hash_password(
            request.json["password"]
        )

        res = self.user_service.add_user(request.json)
        if "password" in res:
            status = 'success'
            del res["password"]
        else:
            status = 'error'
            return {"status": status, "res": res, "message": "error"}, 409
        mail = {
            "recipients": [
                request.json["email"]
            ],
            "sender": "noreply@clo5.io",
            "header": "Welcome to CLO5",
            "body": "Welcome to CLO5.io",
            "htmlbody" : f"<h1>Welcome to CLO5.io</h1><p>You can login to your account user {request.json['name']}</p>"
        }
        self.utils.post_json('http://mailingSvc:5054/v1/mail/send', mail)
        return {"status": status, "res": res, "message": "ok"}, 201


login_model = {
    "email": fields.String(description="Email address", required=True, default='bob@c.lo'),
    "password": fields.String(description="Password", required=True, default='Clo123$'),
}
user_login_model = api.model("LoginModel", login_model)


@api.route("/auth/login")
class UserLogin(Resource):
    """ Connection. """

    def __init__(self, arg):
        super(UserLogin, self).__init__(arg)
        self.jwt_service = JWTService()
        self.utils = Utils()
        self.user_service = UserService()

    @api.expect(user_login_model)
    def post(self):
        """ User login """
        if not self.utils.checkEntityKeysInRequest(login_model, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        email, password = request.json["email"], request.json["password"]

        request.json["password"] = self.jwt_service.hash_password(password)

        user = self.user_service.login(email)
        status = 'none'
        if user:
            pass_match = self.jwt_service.check_password(user["password"], password)
            status = 'success'
        else:
            pass_match = None
            status = 'error'

        if pass_match:
            del user["password"]
            if user['status'] == 'disabled' and user['role'] != 'admin':
                return {"status": status, "res": user, "message": "User disabled and not admin."}, 403
            user["tokens"] = {
                # "access": create_access_token(identity=email),
                # "refresh": create_refresh_token(identity=email),
                # use id instead of email for tokens
                "access": create_access_token(identity=user["_id"]),
                # "refresh": create_refresh_token(identity=user["_id"]),
            }

            status = 'success'
            self.user_service.save_tokens(user["tokens"], additional_claims={"admin": user['role'] == 'admin', 'seller': user['type'] == 'seller'})
            message, status_code = "Login successful.", 200
        else:
            user = []
            status = 'error'
            message, status_code = "Email or Password is wrong.", 401
        return {"status": status, "res": user, "message": message}, status_code

@api.doc(security='token')
@api.route("/auth/logout", methods = ['GET'])
class UserLogout(Resource):
    """docstring for UserLogout."""

    def __init__(self, arg):
        super(UserLogout, self).__init__(arg)
        self.blacklist = BlacklistHelper()

    @jwt_required()
    @api.doc(security='token')
    def get(self):
        """ User logout """
        current_user = get_jwt_identity()
        code, msg = self.blacklist.revoke_user_tokens(current_user)

        return {"status": "success", "msg": msg}, code

# @api.doc(security='token')
# @api.route("/refresh/token")
# class TokenRefresh(Resource):
#     """docstring for TokenRefresh."""

#     def __init__(self, args):
#         super(TokenRefresh, self).__init__(args)

#     # @jwt_refresh_token_required
#     @api.doc(security='token')
#     @jwt_required(refresh=True)
#     def post(self):
#         """ Refresh token - In Progress """
#         current_user = get_jwt_identity()
#         access_token = create_access_token(identity=current_user)

#         self.user_service.save_tokens(access_token, None)

#         return {"status": "success", "access_token": access_token}, 200


@api.doc(security='token')
@api.route("/auth/info")
class UserInfo(Resource):
    """ Prints user info based on given token. """

    def __init__(self, arg):
        super(UserInfo, self).__init__(arg)
        self.blacklist = BlacklistHelper()
        self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    def get(self):
        """ Finds user by given token. """
        current_user = get_jwt_identity()
        app.logger.info('CurrentUser: ' + str(current_user))
        if current_user is None:
            app.logger.error("User is not logged in", current_user)
            return {"status": "error", "message": "Token error"}, 401
        status, data, msg, code = self.user_service.find_user_by_id(current_user)

        return {"status": status, "msg": msg, "data": data}, code
