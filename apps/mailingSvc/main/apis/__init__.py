from flask_restx import Api

from .mailer import api as ns1

api = Api(
    title="",
    version="1.0",
    description="API description",
)

api.add_namespace(ns1)