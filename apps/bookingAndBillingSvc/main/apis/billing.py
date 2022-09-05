from flask_restx import Namespace, Resource, fields

api = Namespace("Billing", description="Billing related APIs")
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from flask import current_app as app
from core.utils import Utils
from main.services.billing_service import BillingService
from main.services.user_service import UserService

_billing = {
    "booking_id": fields.String(description="Booking id", required=True, default='630e8d768813b3468085833c'),
    "recipient_name": fields.String(description="Recipient name", required=True, default='Arthur Morgan'),
    "number_and_street": fields.String(description="Number and street", required=False, default="35 rue de l'opéra"),
    "postal_code": fields.String(description="Postal Code", required=False, default="75001"),
    "city": fields.String(description="City", required=False, default="Paris"),
    "country": fields.String(description="Country", required=False, default='France'),
    "method": fields.String(description="Payment method", required=True, default='card'),
    "provider": fields.String(description="Provider", required=True, default='stripe'),
    "intent": fields.String(description="Payment intent", required=False, default='sale'),
    "client_secret": fields.String(description="Payment intent client secret", required=True, default='pi_1H9xqZ9sx'),
    "status": fields.String(description="Payment intent status", required=True, default='succeeded'),
    "amount": fields.Integer(description="Payment intent amount", required=True, default=199),
    "currency": fields.String(description="Payment intent currency", required=True, default='EUR'),
    "description": fields.String(description="Payment intent description", required=True, default='payment for order'),
    "receipt_email": fields.String(description="Payment intent receipt email", required=True, default='bob@c.lo'),
    "paid": fields.Boolean(description="Payment intent paid", required=True, default=True),
}

billing_model = api.model(
    "BillingModel",
    _billing,
)


@api.route("/billing")
class NewBilling(Resource):
    """docstring for NewBilling."""

    def __init__(self, arg):
        super(NewBilling, self).__init__(arg)
        self.utils = Utils()
        self.billing_service = BillingService()
        self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(billing_model)
    def post(self):
        """ Save new billing object into database """
        if not self.utils.checkEntityKeysInRequest(_billing, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # if data['type'] != 'seller' and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

        # if data['type'] != 'seller' and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

        billing = request.json
        billing['user_id'] = data['_id']
        res, msg, code = self.billing_service.add(billing)

        return {
            "status": self.utils.http_status(code),
            "res": res,
            "message": msg,
        }, code

    # @jwt_required()
    # @api.doc(security='token', parser=None)
    def get(self):
        """ Get list of billinges """
        billinges = self.billing_service.billinges_list()
        return {"status": "success", "res": billinges}, 200

update_billing_model = api.model(
    "BillingUpdateModel",
    _billing,
)


@api.route("/billing/<string:billing_id>")
class Billing(Resource):
    """docstring for Billing."""

    def __init__(self, arg):
        super(Billing, self).__init__(arg)
        self.billing_service = BillingService()
        self.user_service = UserService()

    @jwt_required()
    @api.doc(security='token')
    @api.expect(update_billing_model)
    def put(self, billing_id):
        """ Update billing based on billing_id. """
        if not billing_id:
            api.abort(400, "billing_id is missing.", status="error")

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)
        # if data['_id'] != billing_id and data['role'] != 'admin':
        #     return api.abort(403, f'Not a seller or admin.', status="error", status_code=403)

        status, obj, msg, code = self.billing_service.update_billing(billing_id, request.json, data['_id'])

        return {"status": status, "data": obj, "message": msg}, code

    # @jwt_required()
    # @api.doc(security='token')
    def get(self, billing_id):
        """ Get billing object based on billing_id. """
        billing = self.billing_service.get_billing(billing_id)

        return {"status": "success", "res": billing}, 200

    @jwt_required()
    @api.doc(security='token')
    def delete(self, billing_id):
        """ Delete a billing object based on ID. """
        if not billing_id:
            api.abort(400, f"billing_id is required.", status="error")

        status, data, msg, code = self.user_service.get_user_by_id(get_jwt_identity())
        if status != 'success':
            return api.abort(500, 'Internal error while fetching current user.' + msg, status=status, status_code=500)

        addr = self.billing_service.get_billing(billing_id)
        if addr is None:
            return api.abort(404, 'Internal error while fetching billing.' + msg, status=status, status_code=500)
        # if addr is a list, find the billing that belongs to the user
        if isinstance(addr, list):
            for a in addr:
                if a['ownerUID'] == data['_id']:
                    addr = a
                    break
        if data['_id'] != addr['ownerUID'] and data['role'] != 'admin':
            return api.abort(403, f'Not a owner or admin.', status="error", status_code=403)

        res, msg = self.billing_service.delete_billing(billing_id, data['_id'])

        if res:
            return {"status": "success", "data": res, "message": msg}, 200
        else:
            return api.abort(400, msg, status="error")


# class NullableString(fields.String):
#     __schema_type__ = ['string', 'null']
#     __schema_example__ = 'nullable string'
