from typing import List, Dict, Tuple
from flask import Response, json


class Custom_key_error(Exception):
    def __init__(self,key):
            Exception.__init__(self, f"{key} is missing")


def field_check(fields: Tuple, payload: Dict):
    for field in fields:
        if field not in payload.keys():
            raise Custom_key_error(field)
        payload[field] = str(payload[field]).strip()
    return payload


def custom_response(res):
    """
  Provides a customized response with below content in it.
  """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
    )

from logging import getLogger, StreamHandler, Formatter, INFO


def custom_log(name):
    logger = getLogger(name)
    logger.propagate = False

    # Created handler object
    handler = StreamHandler()
    formatter = Formatter('%(asctime)s - RESTO-CAFE -  %(name)-8s  %(levelname)-s: %(message)s',
                          '%Y-%m-%d %H:%M:%S:%MS')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(INFO)
    return logger
