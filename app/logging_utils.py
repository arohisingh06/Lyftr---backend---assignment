import logging
import uuid
from pythonjsonlogger import jsonlogger

logger = logging.getLogger("api")
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def new_request_id():
    return str(uuid.uuid4())
