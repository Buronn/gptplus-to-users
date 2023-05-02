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
querys = Blueprint("querys", __name__)


@querys.route('/conversations', methods=['GET'])
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
@querys.after_request
def monitor_messages(response):
    return monitoring(response)

@querys.route('/messages/<conversation_id>', methods=['GET'])
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

@querys.route('/messages', methods=['POST'])
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

@querys.route('/metabase', methods=['GET'])
@admin_token
def get_metabase():
    data = token_admin()
    return jsonify({"url":data}), 200

@querys.route('/change-title', methods=['PUT'])
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

@querys.route('/conversations', methods=['POST'])
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

@querys.route('/conversations/<conversation_id>', methods=['DELETE'])
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