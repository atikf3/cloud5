from flask_restx import Namespace, Resource, fields

api = Namespace("Mailer", description="Mail related APIs")
from flask import request, current_app as app

from core.utils import Utils
from flask_mail import Message
from app import mail

msg_model_fields = {
    "recipients": fields.List(fields.String, description="Emails", required=True, default=['contact@talamona.com']),
    "sender": fields.String(description="Email address", required=True, default='noreply@clo5.io'),
    "header": fields.String(description="header", required=True, default='hello'),
    "body": fields.String(description="msg body", required=True, default='this is a test'),
    "htmlbody": fields.String(description="html msg body", required=True, default='<b>this is a html test</b>'),
}
msg_model = api.model("MsgModel", msg_model_fields)


@api.route("/mail/send")
class Mailer(Resource):
    """docstring for Mailer."""

    def __init__(self, arg):
       super(Mailer, self).__init__(arg)
       self.utils = Utils()

    @api.expect(msg_model)
    # @jwt_required()
    # @api.doc(security='token')
    def post(self):
        """ Send email """
        api.logger.debug('A new email is being sent')

        if not self.utils.checkEntityKeysInRequest(msg_model, request):
            return api.abort(400, f'Missing required keys.', status="error", status_code=400)

        msg = Message(request.json["header"], sender=request.json["sender"], recipients=request.json["recipients"])
        msg.body = request.json["body"]
        msg.html = request.json["htmlbody"]
        mail.send(msg)
        return {"status": "success", "message": "ok"}, 200
