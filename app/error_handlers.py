from flask import jsonify
from http import HTTPStatus

class InvalidUsage(Exception):

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = HTTPStatus.BAD_REQUEST
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['description'] = self.message
        return rv


class InternalError(Exception):

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['description'] = self.message
        return rv

