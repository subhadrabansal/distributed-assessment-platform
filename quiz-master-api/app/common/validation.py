from functools import wraps
from flask import request, current_app as app, jsonify
from marshmallow import ValidationError

def abort(status_code, message=None, errors=None):
    response = {
        "success": False,
        "message": message or "",
        "error_message": message or "",
        "data": errors or None
    }
    return jsonify(response), status_code

def validate_request(schema_class):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if data is None:
                app.logger.error("Missing JSON body in request.")
                abort(400, message="Missing JSON body.")
            try:
                schema = schema_class()
                validated_data = schema.load(data)
            except ValidationError as err:
                app.logger.error(f"Validation error: {err.messages}")
                abort(400, message="Validation Error", errors=err.messages)
            kwargs['validated_data'] = validated_data
            app.logger.info(f"Request data validated successfully: {validated_data}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
