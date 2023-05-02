from flask import Blueprint
from routes.decorators import *
views = Blueprint("views", __name__)

@views.route('/')
def hello_world():
    return "<h1>This is a REST API</h1>"

