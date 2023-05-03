import json
from functools import wraps


def jsonify(method):
    """Jsonifies data"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        data = method(self, *args, **kwargs)
        jsonified_data = json.dumps(data)
        return jsonified_data

    return wrapper
