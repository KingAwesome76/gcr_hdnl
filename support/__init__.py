import json
import base64
import random
import string
import re
from datetime import date, datetime


def get_message(filename):
    with open(filename, "r") as source:
        message = source.read()
    if '.xml' in filename:
        return message.encode()
    return json.loads(message)


def mock_ps_object(message, attributes):
    pub_sub = {"message": {"attributes": attributes,
               "data": base64.b64encode(json.dumps(message).encode()).decode()}}
    return pub_sub


def random_string(starter=None, length=None):
    ans = ''.join(random.choices(string.ascii_letters + string.digits, k=30))
    if starter:
        ans = f"{starter}{ans}"
    if length:
        ans = ans[:length]
    return ans


def rx_match(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


def handle_dates(field):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(field, (datetime, date)):
        return field.isoformat()
    return str(field)

