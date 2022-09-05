from flask_restx import Namespace, Resource, fields

api = Namespace("Bookings", description="Bookings related APIs")
from flask import request, current_app as app
from flask_jwt_extended import get_jwt_identity, jwt_required

from core.utils import Utils
from main.services.booking_service import BookingService
from main.services.user_service import UserService

_booking_products = {
    "product_id": fields.String(description="Product", required=True),
    "quantity": fields.Integer(description="Quantity", required=True),
}
_model_booking_products = api.model("ModelBookingProduct", _booking_products)

_booking = {
    "user_id": fields.String(description="User bookinged", required=True),
    "hotel_id": fields.String(description="Delivery address", required=True),
    "room_id": fields.String(description="Delivery address", required=True),
    # "booking_products": fields.Nested(_model_booking_products, as_list=True, allow_null=False),
    "totalAmount": fields.Integer(description="Total Amount", required=True),
    "status": fields.String(description="Status", required=True, default='pending'),
    "date": fields.DateTime(description="Booked At", required=True, default='2020-01-01T00:00:00Z'),
    "date_start": fields.DateTime(description="Booked for", required=True, default='2020-01-01T00:00:00Z'),
    "date_end": fields.DateTime(description="Booked until", required=True, default='2020-01-01T00:00:00Z'),
}
booking_model = api.model( "BookingModel", _booking)

@api.route("/booking")
class NewBooking(Resource):
    """docstring for NewBooking."""

    def __init__(self, arg):
        super(NewBooking, self).__init__(arg)
        self.utils = Utils()
        self.booking_service = BookingService()
        self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(booking_model)
    def post(self):
        """ Save new booking object into database """
        if not self.utils.checkEntityKeysInRequest(_booking, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # TODO: @abdelhanine only staff can create booking
        # if data['type'] != 'seller' and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

        booking = request.json
        booking['ownerUID'] = data['_id']
        res, msg, code = self.booking_service.add(booking)

        return {
            "status": self.utils.http_status(code),
            "res": res,
            "message": msg,
        }, code

    # @jwt_required()
    # @api.doc(security='token', parser=None)
    def get(self):
        """ Get list of bookings """
        bookings = self.booking_service.bookings_list()
        return {"status": "success", "res": bookings}, 200


update_booking_model = api.model(
    "BookingUpdateModel",
    _booking,
)


@api.route("/booking/<string:booking_id>")
class Booking(Resource):
    """docstring for Booking."""

    def __init__(self, arg):
        super(Booking, self).__init__(arg)
        self.booking_service = BookingService()
        self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(update_booking_model)
    def put(self, booking_id):
        """ Update booking based on booking_id. """
        if not booking_id:
            api.abort(400, "booking_id is missing.", status="error")

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        if data['type'] != 'staff' and data['role'] != 'admin':
            return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)
        # if booking status is not pending, return error
        # booking = self.booking_service.get_booking(booking_id)

        # status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        # if status != 'success':
        #     return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        status, obj, msg, code = self.booking_service.update_booking(booking_id, request.json, data['_id'])
        # find user by id
        userStatus, data, userMsg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if userStatus != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # if obj has status key
        # return {"status": 'warning', "data": obj, "message": 'No status'}, code
        # if 'status' in request.json and request.json["status"] != "pending":
        #     msg = Message(f'Booking {data["_id"] or None} status changed',
        #     sender="noreply@mls.com",
        #     recipients=[data['email']])
        #     msg.body = "Your booking status has been changed to " + (request.json["status"])
        #     msg.html = "<b>Your booking status has been changed to " + request.json["status"] + "</b>"
        #     mail.send(msg)
        # else:
        #     return {"status": 'warning', "data": 'No', "message": 'No status'}, code
        return {"status": status, "data": request.json, "message": userMsg}, code

    # @jwt_required()
    # @api.doc(security='token')
    def get(self, booking_id):
        """ Get booking object based on booking_id. """
        booking = self.booking_service.get_booking(booking_id)

        return {"status": "success", "res": booking}, 200

    @jwt_required()
    @api.doc(security='token')
    def delete(self, booking_id):
        """ Delete a booking object based on ID. """
        if not booking_id:
            api.abort(400, f"booking_id is required.", status="error")

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        if data['type'] != 'staff' and data['role'] != 'admin':
            return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

        res, msg = self.booking_service.delete_booking(booking_id, data['_id'])

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")
