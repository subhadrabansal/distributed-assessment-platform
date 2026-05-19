from functools import wraps
from flask_jwt_extended import get_jwt_identity
import json

def roles_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = json.loads(get_jwt_identity())
            user_roles = identity.get('roles', '').split(',')

            if not any(role in allowed_roles for role in user_roles):
               
                return {"message": f"Access forbidden: Allowed roles - {', '.join(allowed_roles)}"}, 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
