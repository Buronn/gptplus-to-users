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
contacts = Blueprint("contacts", __name__)

@contacts.route('/')
def hello_world():
    return "<h1>This is a REST API</h1>"

@contacts.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    answer = login_check(data)
    return answer

@contacts.route('/logout', methods=['POST'])
@black_list_token
def logout():
    return {'message': 'Logout successful'}

@contacts.route('/register', methods=['POST'])
@admin_token
def register():
    data = request.get_json()
    answer = register_check(data)
    return answer


@contacts.route('/change-password', methods=['PUT'])
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

@contacts.route('/users', methods=['GET'])
@admin_token
def get_users():
    data = get_users_list()
    return data

@contacts.route('/delete-user', methods=['POST'])
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

@contacts.route('/check-login', methods=['GET'])
@user_token
def check():
    return {'message': 'Check successful'}, 200

@contacts.route('/conversations', methods=['GET'])
@user_token
def get_conversations():
    data=chat.gpt_conversations()
    # Filter conversations by user
    user_id = get_user_id()
    if user_id != 1:
        conversation = []
        for conv in data['items']:
            user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
            if conv['id'] in [c.id for c in user_conversations]:
                conversation.append(conv)
        data['items'] = conversation
    return data, 200
@contacts.after_request
def monitor_messages(response):
    return monitoring(response)

@contacts.route('/messages/<conversation_id>', methods=['GET'])
@user_token
def get_messages(conversation_id):
    user_id = get_user_id()
    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
        if conversation_id not in [c.id for c in user_conversations]:
            return jsonify({"error": "Not allowed"}), 403
    if not conversation_id:
        return jsonify({"error": "Missing data"}), 400
    else:
        data=chat.gpt_conversation(conversation_id)
        return data, 200

@contacts.route('/messages', methods=['POST'])
@user_token
def send_message():
    user_id = get_user_id()
    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
        if request.json['conversation_id'] not in [c.id for c in user_conversations]:
            return jsonify({"error": "Not allowed"}), 403
    if not request.json:
        return jsonify({"error": "Missing data"}), 400
    else:
        conversation_id = request.json['conversation_id']
        parent_message_id = request.json['parent_message_id']
        message = request.json['message']
        def send_data(line):
            response = make_response(line + b'\n')
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['X-Accel-Buffering'] = 'no'
            return response
        chat.gpt_response(conversation_id, parent_message_id, message, send_data)
        return jsonify({"message":"Procesamiento completo."}), 200

@contacts.route('/metabase', methods=['GET'])
@admin_token
def get_metabase():
    data = token_admin()
    return jsonify({"url":data}), 200

@contacts.route('/change-title', methods=['PUT'])
@user_token
def change_title():
    user_id = get_user_id()
    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
        if request.json['conversation_id'] not in [c.id for c in user_conversations]:
            return jsonify({"error": "Not allowed"}), 403
    if not request.json:
        return jsonify({"error": "Missing data"}), 400
    else:
        conversation_id = request.json['conversation_id']
        title = request.json['title']
        chat.gpt_change_title(conversation_id, title)
    return {'message': 'Change title successful'}, 200

@contacts.route('/conversations', methods=['POST'])
@user_token
def new_conversation():
    try:
        current_id = get_user_id()
        if not request.json:
            return jsonify({"error": "Missing data"}), 400
        else:
            message = request.json['message']
            def send_data(line):
                response = make_response(line + b'\n')
                response.headers['Content-Type'] = 'text/plain'
                response.headers['Cache-Control'] = 'no-cache'
                response.headers['X-Accel-Buffering'] = 'no'
                return response
            chat.gpt_new_conversation(message, send_data, store_conversation_id, current_id)
            return jsonify({"message":"Procesamiento completo."}), 200
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error processing request"}), 500

@contacts.route('/conversations/<conversation_id>', methods=['DELETE'])
@user_token
def delete_conversation(conversation_id):
    if not conversation_id:
        return jsonify({"error": "Missing data"}), 400
    else:
        chat.gpt_delete_conversation(conversation_id)
        conversation = Preguntas.query.filter_by(id=conversation_id).first()
        db.session.delete(conversation)
        db.session.commit()

    return {'message': 'Delete conversation successful'}, 200