import json
from core.utils import Utils
from flask_restx import Namespace, Resource, fields

api = Namespace("User", description="User related APIs")
from flask import Response, request, current_app as app
from flask_jwt_extended import get_jwt_identity, jwt_required

from main.services.jwt_service import JWTService
from main.services.user_service import UserService

user_model = {
    "name": fields.String(description="Name of the user", required=True, default='clo'),
    "email": fields.String(description="Email address", required=True, default='clo@c.lo'),
    "password": fields.String(description="password", required=True, default='Clo123$'),
}
user_apiModel = api.model("UserCreateModel", user_model)


@api.route("/user/<user_id>")
class User(Resource):
    """docstring for User."""

    def __init__(self, arg):
        super(User, self).__init__(arg)
        self.jwt_service = JWTService()
        self.user_service = UserService()
        self.arg = arg

    @jwt_required()
    @api.doc(security='token')
    def get(self, user_id):
        """ Get user object by _id. ex: 622b645e845d27a34bb1aed6 """
        current_user = get_jwt_identity()
        if current_user is None:
            app.logger.error("User is not logged in", current_user)
            return {"status": "error", "message": "Token error"}, 401
        msg = "Current user is " + current_user
        status, res, msg, code = self.user_service.get_user_by_id(user_id)

        return {"status": status, "message": msg, "res": res}, code

    @jwt_required()
    @api.doc(security='token')
    @api.expect(user_apiModel)
    def put(self, user_id):
        """ Update User profile by _id """
        if not user_id:
            api.abort(400, "User _id is missing.", status="error")

        if "password" in request.json and request.json["password"] != "":
            request.json["password"] = self.jwt_service.hash_password(
                request.json["password"]
            )

        status, usr, msg, code = self.user_service.update_user(user_id, request.json, get_jwt_identity())
        if status == "success" and usr['status'] == 'disabled':
            app.logger.info('User is disabled, revoking tokens.')
            self.jwt_service.revoke_user_tokens(user_id)

        return {"status": status, "data": usr, "message": msg}, code

    @api.doc(security='token')
    @jwt_required()
    def delete(self, user_id):
        """ Delete User based on user_id """
        if not user_id:
            api.abort(400, f"User _id is required.", status="error")

        res, msg = self.user_service.delete_user(user_id)

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")


@api.route("/users")
class UserList(Resource):
    """docstring for UserList."""

    def __init__(self, arg):
        super(UserList, self).__init__(arg)
        self.jwt_service = JWTService()
        self.user_service = UserService()
        self.utils = Utils()
        self.arg = arg

    @jwt_required()
    @api.doc(security='token')
    def get(self):
        """ Get list of users """
        users = self.user_service.user_list()

        return {"status": "success", "res": users}, 200

    @api.expect(user_apiModel)
    @jwt_required()
    @api.doc(security='token')
    # @role_required('admin')
    def post(self):
        """ Adds new User (Need admin perms). """
        api.logger.debug('Adding new user')

        if not self.utils.checkEntityKeysInRequest(user_model, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        request.json["password"] = self.jwt_service.hash_password(
            request.json["password"]
        )

        res = self.user_service.add_user_admin(request.json, get_jwt_identity())
        if "password" in res:
            status = 'success'
            del res["password"]
        else:
            status = 'error'
            return {"status": status, "res": res, "message": "user not added"}, 409

        return {"status": status, "res": res, "message": "added"}, 201
