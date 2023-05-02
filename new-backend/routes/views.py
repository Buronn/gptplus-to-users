from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from models.contact import Users, Preguntas, Requests, LogoutToken
from utils.db import db
from werkzeug.exceptions import Unauthorized
import logging 
import os, jwt, bcrypt, datetime
import time
from functools import wraps
import chat.functions as chat
from routes.decorators import *
views = Blueprint("views", __name__)

@views.route('/')
def hello_world():
    return "<h1>This is a REST API</h1>"

