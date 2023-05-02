from flask import Blueprint, request, jsonify
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

