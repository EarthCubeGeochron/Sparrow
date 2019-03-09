# Simplejson's encoder supports decimals
from simplejson import JSONEncoder as SimpleJSONEncoder
from datetime import datetime

class JSONEncoder(SimpleJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        super().default(obj)
