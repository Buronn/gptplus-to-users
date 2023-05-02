from flask import Blueprint, request, jsonify
from models.contact import Users
from utils.db import db
import bcrypt
import chat.functions as chat
from routes.decorators import *
auth = Blueprint("auth", __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    answer = login_check(data)
    return answer

@auth.route('/logout', methods=['POST'])
@black_list_token
def logout():
    return {'message': 'Logout successful'}

@auth.route('/register', methods=['POST'])
@admin_token
def register():
    data = request.get_json()
    answer = register_check(data)
    return answer


@auth.route('/change-password', methods=['PUT'])
@user_token
def change_password():
    data = request.get_json()
    user = Users.query.filter_by(id=get_user_id()).first()
    password = data['password']

    if not password:
        return jsonify({"error": "Missing data"}), 400
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Wrong password"}), 400
    
    new_password = data['new_password']
    if not new_password:
        return jsonify({"error": "Missing data"}), 400
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    user.password = hashed_password.decode('utf-8')
    db.session.commit()

    return {'message': 'Password changed successfully'}, 200


@auth.route('/check-login', methods=['GET'])
@user_token
def check():
    return {'message': 'Check successful'}, 200
