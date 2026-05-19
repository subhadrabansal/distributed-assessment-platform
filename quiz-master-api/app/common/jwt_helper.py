import json
from flask_jwt_extended import get_jwt_identity

def extract_user_info_from_jwt():
    identity_json = get_jwt_identity()
    try:
        identity = json.loads(identity_json) if isinstance(identity_json, str) else identity_json
        return identity.get('id'), identity.get('roles')
    except Exception:
        return None, None
