from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request


def get_real_ip():
    return request.headers.get("X-Forwarded-For", get_remote_address()).split(",")[0].strip()


limiter = Limiter(key_func=get_real_ip)
