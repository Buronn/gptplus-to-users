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
users = Blueprint("users", __name__)


@users.route('/users', methods=['GET'])
@admin_token
def get_users():
    data = get_users_list()
    return data

@users.route('/delete-user', methods=['POST'])
@admin_token
def delete_user():
    if not request.json:
        return jsonify({"error": "Missing data"}), 400
    else:
        id = request.json['id']
        if not id:
            return jsonify({"error": "Missing data"}), 400
        else:
            answer = delete_user_check(id)
            return answer

