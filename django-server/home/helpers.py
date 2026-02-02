import re

def normalise_string(text):
    return re.sub(r'[^\w]', '', text, flags=re.UNICODE)