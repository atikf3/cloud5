from xml.dom.minidom import Element
from flask_restx import Namespace, Resource, fields

api = Namespace("Wishlist", description="Wishlists related APIs")
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from core.utils import Utils
from main.services.wishlist_service import WishlistService
from main.services.user_service import UserService

_wishlist = {
    "products": fields.List(fields.String(description="Product ID", required=True, default='null'), default=[]),
    "owner_id": fields.String(description="Wishlist owner ID", required=False, default='Anonymous'),
    "isPublic": fields.Boolean(description="Is wishlist public", required=False, default=True),
}
wishlist_model = api.model("WishlistModel", _wishlist)


@api.route("/wishlist")
class NewWishlist(Resource):
    """ Wishlist resource, managing user product wishlist. """

    def __init__(self, arg):
        super(NewWishlist, self).__init__(arg)
        self.utils = Utils()
        self.wishlist_service = WishlistService()
        self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(wishlist_model)
    def post(self):
        """ Add wish to DB """
        if not self.utils.checkEntityKeysInRequest(_wishlist, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)
        # check if wishlist already exists
        user_id = get_jwt_identity()
        wishlist = self.wishlist_service.wishlists_list_for_user(user_id)
        if len(wishlist) > 0:
            wishlist = wishlist[0]
        if not wishlist or "products" not in wishlist:
            wishlist = request.json
            wishlist["user_id"] = user_id
            res, msg, code = self.wishlist_service.add(wishlist)
        else:
            wishlist["user_id"] = user_id
            wishlist["products"] = list(set(wishlist["products"] + request.json["products"]))
            status, res, msg, code = self.wishlist_service.update_wishlist(wishlist['_id'], wishlist)
        return {
            "status": self.utils.http_status(code),
            "res": res,
            "message": msg,
        }, code

    @jwt_required()
    @api.doc(id='get_wishlists',security='token', parser=None)
    def get(self):
        """ Get list of wishlists (Admin) """
        # status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        # if status != 'success':
        #     return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # if data['type'] != 'seller' and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)
        wishlists = self.wishlist_service.wishlists_list()
        return {"status": "success", "res": wishlists}, 200

    @jwt_required()
    @api.doc(id='get_user_wishlist', security='token')
    def get(self):
        """ Get user wishlist """
        wishlist = self.wishlist_service.wishlists_list_for_user(get_jwt_identity())
        if len(wishlist) > 0:
            wishlist = wishlist[0]
        return {"status": "success", "res": wishlist}, 200
    
    @jwt_required()
    @api.doc(security='token')
    @api.expect(wishlist_model)
    def put(self):
        """ Update wishlist based on wishlist_id. """
        wishlist = self.wishlist_service.wishlists_list_for_user(get_jwt_identity())
        if len(wishlist) > 0:
            wishlist = wishlist[0]
        if not wishlist:
            return api.abort(404, f'Wishlist not found.', status="error", status_code=404)
        wishlist['products'] = request.json['products']
        status, obj, msg, code = self.wishlist_service.update_wishlist(wishlist['_id'], wishlist)

        return {"status": status, "data": obj, "message": msg}, code

    @jwt_required()
    @api.doc(security='token')
    def delete(self):
        """ Prune user wishlist. """
        wishlist = self.wishlist_service.wishlists_list_for_user(get_jwt_identity())
        wishlist['products'] = []
        res, msg = self.wishlist_service.update_wishlist(wishlist['_id'], wishlist)

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")



# @api.route("/wishlist/<string:wishlist_id>")
# class Wishlist(Resource):
#     """docstring for Wishlist."""

#     def __init__(self, arg):
#         super(Wishlist, self).__init__(arg)
#         self.wishlist_service = WishlistService()
#         self.user_service = UserService()

#     @jwt_required()
#     @api.doc(security='token')
#     @api.expect(wishlist_model)
#     def put(self, wishlist_id):
#         """ Update wishlist based on wishlist_id. """
#         if not wishlist_id:
#             api.abort(400, "wishlist_id is missing.", status="error")

#         status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
#         if status != 'success':
#             return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
#         if data['type'] != 'seller' and data['role'] != 'admin':
#             return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

#         status, obj, msg, code = self.wishlist_service.update_wishlist(wishlist_id, request.json, data['_id'])

#         return {"status": status, "data": obj, "message": msg}, code

#     # @jwt_required()
#     # @api.doc(security='token')
#     def get(self, wishlist_id):
#         """ Get wishlist object based on wishlist_id. """
#         wishlist = self.wishlist_service.get_wishlist(wishlist_id)

#         return {"status": "success", "res": wishlist}, 200


#     @jwt_required()
#     @api.doc(security='token')
#     def delete(self, wishlist_id):
#         """ Prune user wishlist. """
#         # if not wishlist_id:
#         #     api.abort(400, f"wishlist_id is required.", status="error")

#         status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
#         if status != 'success':
#             return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
#         if data['type'] != 'seller' and data['role'] != 'admin':
#             return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

#         res, msg = self.wishlist_service.delete_wishlist(wishlist_id, data['_id'])

#         if res:
#             return {"status": "success", "data": res, "message": msg}, 200
#         else:
#             return api.abort(400, msg, status="error")

    # @jwt_required()
    # @api.doc(security='token')
    # def delete(self, wishlist_id):
    #     """ Delete a wishlist based on ID. """
    #     if not wishlist_id:
    #         api.abort(400, f"wishlist_id is required.", status="error")

    #     status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
    #     if status != 'success':
    #         return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
    #     if data['type'] != 'seller' and data['role'] != 'admin':
    #         return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

    #     res, msg = self.wishlist_service.delete_wishlist(wishlist_id, data['_id'])

    #     if res:
    #         return {"status": "success", "data": res, "message": msg}, 200
    #     else:
    #         return api.abort(400, msg, status="error")