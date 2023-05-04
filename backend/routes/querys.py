from flask import Blueprint, request, jsonify, make_response
from models.contact import Users, Preguntas, Requests, LogoutToken, Messages
from utils.db import db
import logging 
import chat.functions as chat
from routes.decorators import *
querys = Blueprint("querys", __name__)

def message_to_dict(message):
    # Ignore if role is system
    if message.role == "system":
        return None
    return {"role": message.role, "content": message.content, "date": message.date}
@querys.after_request
def monitor_messages(response):
    return monitoring(response)
@querys.route('/conversations', methods=['GET'])
@user_token
def get_conversations():
    user_id = get_user_id()

    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
    else:
        user_conversations = Preguntas.query.all()

    conversations_data = []
    for conversation in user_conversations:
        if conversation.deleted:
            continue
        conversation_id = conversation.id
        title = conversation.title
        date = conversation.date
        messages = Messages.query.filter_by(pregunta_id=conversation_id).all()
        messages_data = [message_to_dict(msg) for msg in messages]

        conversations_data.append({
            "id": conversation_id,
            "title": title,
            "date": date,
            "messages": messages_data
        })

    return jsonify({"items": conversations_data}), 200

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
        # Obtener las conversaciones de la base de datos
        conversation = Preguntas.query.filter_by(id=conversation_id).first()
        title = conversation.title
        # Is deleted?
        if conversation.deleted:
            return jsonify({"error": "Conversation deleted"}), 403
        messages = Messages.query.filter_by(pregunta_id=conversation_id).all()
        # Obtener role, content y date
        messages_data = [message_to_dict(msg) for msg in messages]
        return jsonify({"conversation_id": conversation_id, "messages": messages_data, "title": title}), 200

@querys.route('/conversations', methods=['POST'])
@user_token
def new_conversation():
    try:
        current_id = get_user_id()
        if not request.json:
            return jsonify({"error": "Missing data"}), 400
        else:
            message = request.json['message']
            response_json = chat.gpt_new_conversation(message, current_id) # TODO: Add system message and model
            response = make_response(response_json.encode() + b'\n')
            return response, 200
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error processing request"}), 500

@querys.route('/messages', methods=['POST'])
@user_token
def send_message():
    try:
        user_id = get_user_id()
        if user_id != 1:
            user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
            if request.json['conversation_id'] not in [c.id for c in user_conversations]:
                return jsonify({"error": "Not allowed"}), 403

        if not request.json:
            return jsonify({"error": "Missing data"}), 400
        else:
            conversation_id = request.json['conversation_id']
            message = request.json['message']
            response_json = chat.gpt_continue_conversation(conversation_id, message) # TODO: Add model

            response = make_response(response_json.encode() + b'\n')

            return response, 200
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error processing request"}), 500

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




@querys.route('/conversations/<conversation_id>', methods=['DELETE'])
@user_token
def delete_conversation(conversation_id):
    if not conversation_id:
        return jsonify({"error": "Missing data"}), 400
    else:
        chat.gpt_delete_conversation(conversation_id)

    return {'message': 'Delete conversation successful'}, 200

@querys.route('/metabase', methods=['GET'])
@admin_token
def get_metabase():
    data = token_admin()
    return jsonify({"url":data}), 200