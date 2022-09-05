from flask_restx import Namespace, Resource, fields

api = Namespace("Rooms", description="Rooms related APIs")
from flask import request, current_app as app
from flask_jwt_extended import get_jwt_identity, jwt_required

from core.utils import Utils
from main.services.room_service import RoomService
# from flask_mail import Message
# from app import mail

_room_hotels = {
    "hotel_id": fields.String(description="Product", required=True),
    "quantity": fields.Integer(description="Quantity", required=True),
}
_model_room_hotels = api.model("ModelRoomProduct", _room_hotels)

_room = {
    "hotel_id": fields.String(description="Hotel id", required=True),
    "hotel_name": fields.String(description="Hotel name", required=False),
    "room_name": fields.String(description="room name", required=True, default='Standard suite'),
    "hotel_name": fields.String(description="Hotel name", required=False),
    "price": fields.Integer(description="beds available", required=True),
    "facilities_facility": fields.List(fields.String, description="options", required=True, default=['Free WiFi', 'Flat-screen TV', 'air-conditioner','Private bathroom', 'Garden view', 'Coffee machine']),
    "facilities_other": fields.List(fields.String, description="options", required=True, default=['Toilet', 'Bath or shower', 'Towels', 'Linen', 'Desk', 'Toaster', 'Cable channels']),
    # "room_hotels": fields.Nested(_model_room_hotels, as_list=True, allow_null=False)
    "beds": fields.Integer(description="beds available", required=True, default=1),
    "persons": fields.Integer(description="max persons in the room", required=True, default=2)
}
room_model = api.model( "RoomModel", _room)

@api.route("/room")
class NewRoom(Resource):
    """docstring for NewRoom."""

    def __init__(self, arg):
        super(NewRoom, self).__init__(arg)
        self.utils = Utils()
        self.room_service = RoomService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(room_model)
    def post(self):
        """ Save new room object into database """
        if not self.utils.checkEntityKeysInRequest(_room, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        # status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        # if status != 'success':
        #     return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # TODO: @abdelhanine only acheteur can create room
        # if data['type'] != 'seller' and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

        room = request.json
        res, msg, code = self.room_service.add(room)

        return {
            "status": self.utils.http_status(code),
            "res": res,
            "message": msg,
        }, code

    # @jwt_required()
    # @api.doc(security='token', parser=None)
    def get(self):
        """ Get list of rooms """
        rooms = self.room_service.rooms_list()
        return {"status": "success", "res": rooms}, 200


update_room_model = api.model(
    "RoomUpdateModel",
    _room,
)


@api.route("/room/<string:room_id>")
class Room(Resource):
    """docstring for Room."""

    def __init__(self, arg):
        super(Room, self).__init__(arg)
        self.room_service = RoomService()
        # self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(update_room_model)
    def put(self, room_id):
        """ Update room based on room_id. """
        if not room_id:
            api.abort(400, "room_id is missing.", status="error")

        # status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        # if status != 'success':
        #     return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # if data['type'] != 'seller' and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)
        # if room status is not pending, return error
        # room = self.room_service.get_room(room_id)

        # status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        # if status != 'success':
        #     return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        status, obj, msg, code = self.room_service.update_room(room_id, request.json)
        # find user by id
        # userStatus, data, userMsg, code = self.user_service.get_user_by_id(get_jwt_identity())
        # if userStatus != 'success':
        #     return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # if obj has status key
        # return {"status": 'warning', "data": obj, "message": 'No status'}, code
        # if 'status' in request.json and request.json["status"] != "pending":
        #     msg = Message(f'Room {data["_id"] or None} status changed',
        #     sender="noreply@mls.com",
        #     recipients=[data['email']])
        #     msg.body = "Your room status has been changed to " + (request.json["status"])
        #     msg.html = "<b>Your room status has been changed to " + request.json["status"] + "</b>"
        #     mail.send(msg)
        # else:
        #     return {"status": 'warning', "data": 'No', "message": 'No status'}, code
        return {"status": status, "data": request.json, "message": 'he'}, code

    # @jwt_required()
    # @api.doc(security='token')
    def get(self, room_id):
        """ Get room object based on room_id. """
        room = self.room_service.get_room(room_id)

        return {"status": "success", "res": room}, 200

    @jwt_required()
    @api.doc(security='token')
    def delete(self, room_id):
        """ Delete a room object based on ID. """
        if not room_id:
            api.abort(400, f"room_id is required.", status="error")


        res, msg = self.room_service.delete_room(room_id)

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")
