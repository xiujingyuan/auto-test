from flask import Blueprint

api_nacos = Blueprint('api_nacos', __name__)

from . import nacos_api
