import os
import json
import uuid
import sqlalchemy
import spacy
import openai

from models.contact import Messages, Preguntas, Tokens
from utils.db import db

nlp = spacy.load("es_core_news_sm")
openai.api_key = os.environ['AUTH_TOKEN']
SYSTEM_MESSAGE = "Sigues las siguientes reglas para responder:\n" \
                    "1. Sé conciso\n" \
                    "2. Si te piden código, no expliques, solo envía el código\n"

def api_request(model, messages, stream=False):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5,
        stream=stream,
    )
    return response


def extract_keywords(text):
    keywords = []
    doc = nlp(text)
    for token in doc:
        if token.is_alpha and (token.pos_ in ("NOUN", "PROPN", "ADJ", "VERB")):
            keywords.append(token.lemma_.lower())
    return keywords


def gpt_new_conversation(initial_message, user_id, system_message=SYSTEM_MESSAGE, model_name="gpt-3.5-turbo"):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": initial_message}
    ]
    response = api_request(model=model_name, messages=messages)

    conversation_id = str(uuid.uuid4())
    for _ in range(10):
        try:
            print("Tokens used in", conversation_id, ":", "\n", 
                  "\t Prompt", response['usage']['prompt_tokens'], "\n", 
                  "\t Completion Tokens", response['usage']['completion_tokens'], "\n",
                  "\t Total Tokens", response['usage']['total_tokens'])

            pregunta = Preguntas(id=conversation_id, user_id=user_id, deleted=False)
            tokens = Tokens(pregunta_id=conversation_id, token=response['usage']['total_tokens'])

            system_msg = Messages(pregunta_id=conversation_id, role="system", content=system_message)
            initial_msg = Messages(pregunta_id=conversation_id, role="user", content=initial_message)
            assistant_msg = Messages(pregunta_id=conversation_id, role="assistant", content=response['choices'][0]['message']['content'])
            
            pregunta.messages.extend([system_msg, initial_msg, assistant_msg])

            db.session.add_all([pregunta, tokens, system_msg, initial_msg, assistant_msg])
            db.session.commit()
            break
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            conversation_id = str(uuid.uuid4())

    response_json = json.dumps(response)
    return response_json


def gpt_continue_conversation(conversation_id, message, model_name="gpt-3.5-turbo", economic=False):
    conversation = Preguntas.query.filter_by(id=conversation_id).first()
    if not conversation:
        return

    messages = Messages.query.filter_by(pregunta_id=conversation_id).all()
    messages_data = [{"role": msg.role, "content": msg.content} for msg in messages]
    messages_data.append({"role": "user", "content": message})
    message_obj = Messages(pregunta_id=conversation_id, role='user', content=message)
    db.session.add(message_obj)

    recent_conversation = [{"role": msg["role"], "content": msg["content"]} for msg in messages_data[-2:]]
    prompt = recent_conversation

    if economic:
        keywords = []
        for msg in messages_data[:-2]:  # Excluir las dos últimas interacciones (las más recientes)
            keywords.extend(extract_keywords(msg["content"]))
        keywords_text = "Palabras clave utilizadas anteriormente: " + ", ".join(set(keywords)) + "."
        prompt = [{"role": "assistant", "content": keywords_text}] + recent_conversation

    response = api_request(model=model_name, messages=prompt)

    choice = response['choices'][0]

    token_usage = Tokens(pregunta_id=conversation_id, token=response['usage']['total_tokens'])
    db.session.add(token_usage)
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
