from flask_restx import Api

from .hotel import api as ns1
from .room import api as ns2

api = Api(
    title="",
    version="1.0",
    description="API description",
)

api.add_namespace(ns1)
api.add_namespace(ns2)
