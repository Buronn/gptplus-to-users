import os
import sqlalchemy
import uuid
import json
from models.contact import Messages, Preguntas
from utils.db import db
import openai

openai.api_key = os.environ['AUTH_TOKEN']

def api_request(model, messages, stream=False):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=256,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stream=stream
    )
    
    return response

def gpt_new_conversation(initial_message, user_id):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": initial_message
        }
    ]
    response = api_request(model="gpt-3.5-turbo", messages=messages)

    # Utiliza un bucle while para seguir intentando hasta que se genere un UUID único
    cont = 0
    while cont < 10:
        try:
            conversation_id = str(uuid.uuid4())
            pregunta = Preguntas(id=conversation_id, user_id=user_id, deleted=False)
            db.session.add(pregunta)

            # Crear y guardar objetos Messages para el mensaje inicial, el mensaje del sistema y la respuesta del asistente
            system_msg = Messages(pregunta_id=conversation_id, role="system", content="You are a helpful assistant.")
            initial_msg = Messages(pregunta_id=conversation_id, role="user", content=initial_message)
            assistant_msg = Messages(pregunta_id=conversation_id, role="assistant", content=response['choices'][0]['message']['content'])

            pregunta.messages.extend([system_msg, initial_msg, assistant_msg])

            db.session.commit()
            break  # Sal del bucle si la inserción en la base de datos es exitosa
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            cont += 1
            continue  # Inténtalo de nuevo si el UUID ya existe en la base de datos
    response_json = json.dumps(response)
    return response_json


def gpt_continue_conversation(conversation_id, message):
    conversation = Preguntas.query.filter_by(id=conversation_id).first()
    if not conversation:
        return

    messages = Messages.query.filter_by(pregunta_id=conversation_id).all()
    messages_data = [{"role": msg.role, "content": msg.content} for msg in messages]

    messages_data.append({"role": "user", "content": message})
    message_obj = Messages(pregunta_id=conversation_id, role='user', content=message)
    response = api_request(model="gpt-3.5-turbo", messages=messages_data)

    choice = response['choices'][0]
    message_obj = Messages(pregunta_id=conversation_id, role='assistant', content=choice['message']['content'])
    db.session.add(message_obj)
    db.session.commit()

    response_json = json.dumps(response)
    return response_json


def gpt_delete_conversation(conversation_id):
    conversation = Preguntas.query.filter_by(id=conversation_id).first()
    if conversation:
        conversation.deleted = True
        db.session.commit()
        return {"status": "success", "message": "Conversation marked as deleted"}
    else:
        return {"status": "error", "message": "Conversation not found"}

def gpt_change_title(conversation_id, title):
    conversation = Preguntas.query.filter_by(id=conversation_id).first()
    if conversation:
        conversation.title = title
        db.session.commit()
        return {"status": "success", "message": "Title changed successfully"}
    else:
        return {"status": "error", "message": "Conversation not found"}
