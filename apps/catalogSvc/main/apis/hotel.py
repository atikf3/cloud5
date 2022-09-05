from flask_restx import Namespace, Resource, fields

api = Namespace("Hotels", description="Hotels related APIs")
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from core.utils import Utils
from main.services.hotel_service import HotelService

_review = {
    "rate": fields.Integer(description="rate, from 0 to 5 stars", required=False, default='5'),
    "review": fields.String(description="review", required=False, default='Good'),
    "author_name": fields.String(description="review_author_name", required=False, default='Anonymous'),
    "author_id": fields.String(description="review_author_id", required=False, default='Anonymous'),
    "date": fields.DateTime(description="review_date", required=False, default='2020-01-01T00:00:00Z')
}
review_model = api.model("ReviewModel", _review)

_property = {
    "hotel_name": fields.String(description="Hotel name", required=True, default='Novotel'),
    "stars": fields.Integer(description="stars", required=True, default=3),
    "city": fields.String(description="paris", required=True, default='Paris'),
    "address": fields.String(description="17 Pl. Dauphine, 75001 Paris", required=True, default='Paris'),
    "status": fields.String(description="enabled, disabled", required=True, default='enabled'),
    "phone": fields.String(description="01 12 34 56 78", required=False, default='enabled'),
    "creation_date": fields.DateTime(description="review_date", required=False, default='2020-01-01T00:00:00Z'),
    # "reviews": fields.Nested(review_model, as_list=True, allow_null=True),
    # "reviews": fields.Nested(review_model, as_list=True, allow_null=True),
}
hotel_model = api.model( "HotelModel", _property)


@api.route("/hotel")
class NewHotel(Resource):
    """docstring for NewHotel."""

    def __init__(self, arg):
        super(NewHotel, self).__init__(arg)
        self.utils = Utils()
        self.hotel_service = HotelService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(hotel_model)
    def post(self):
        """ Save new hotel object into database """
        if not self.utils.checkEntityKeysInRequest(_property, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        hotel = request.json
        res, msg, code = self.hotel_service.add(hotel)

        return {
            "status": self.utils.http_status(code),
            "res": res,
            "message": msg,
        }, code

    # @jwt_required()
    # @api.doc(security='token', parser=None)
    def get(self):
        """ Get list of hotels """
        hotels = self.hotel_service.hotels_list()
        return {"status": "success", "res": hotels}, 200


update_property_model = api.model(
    "HotelUpdateModel",
    _property,
)


@api.route("/hotel/<string:hotel_id>")
class Hotel(Resource):
    """docstring for Hotel."""

    def __init__(self, arg):
        super(Hotel, self).__init__(arg)
        self.hotel_service = HotelService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(update_property_model)
    def put(self, hotel_id):
        """ Update hotel based on hotel_id. """
        if not hotel_id:
            api.abort(400, "hotel_id is missing.", status="error")

        status, obj, msg, code = self.hotel_service.update_property(hotel_id, request.json)

        # if hotel_id is in a wishlist, return error
        haas = self.wishlist_service.get_wishlists_by_property_id(hotel_id)
        
        return {"status": status, "data": haas, "message": msg}, code
        return {"status": status, "data": obj, "message": msg}, code

    # @jwt_required()
    # @api.doc(security='token')
    def get(self, hotel_id):
        """ Get hotel object based on hotel_id. """
        hotel = self.hotel_service.get_property(hotel_id)

        return {"status": "success", "res": hotel}, 200

    @jwt_required()
    @api.doc(security='token')
    def delete(self, hotel_id):
        """ Delete a hotel object based on ID. """
        if not hotel_id:
            api.abort(400, f"hotel_id is required.", status="error")

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        if data['type'] != 'staff' and data['role'] != 'admin':
            return api.abort(403, f'Not a staff or admin.', status="error", status_code=403)

        res, msg = self.hotel_service.delete_property(hotel_id, data['_id'])

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")


# class NullableString(fields.String):
#     __schema_type__ = ['string', 'null']
#     __schema_example__ = 'nullable string'
