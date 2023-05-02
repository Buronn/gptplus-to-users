import requests
import os
import uuid
import json

# Models: text-davinci-002-render-sha gpt-4

base_url = "https://chat.openai.com/backend-api/"
auth_token = os.environ['AUTH_TOKEN']
puid_user = os.environ['PUID_USER']
# headers = {
#     f'authorization': f'Bearer {auth_token}',
#     f'cookie': f'puid_user={puid_user}; token={cookie_token}',
# }

headers = {
    "cookie": f"_puid={puid_user}",
    "authorization": f"Bearer {auth_token}"
}


def gpt_conversations():
    url = base_url + "conversations"+"?offset=0&limit=100"
    try:
        response = requests.get(url, headers=headers)
        print(response.json())
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def gpt_conversation(conversation_id):
    url = base_url + f"conversation/{conversation_id}"
    response = requests.get(url, headers=headers)
    return response.json()

def gpt_new_conversation(initial_message, callback, conversation_id_callback, user_id):
    url = base_url + "conversation"
    entered = False
    uuid_01 = str(uuid.uuid4())
    data = {
        "action": "next",
        "messages":
        [
            {
                "author": {"role": "user"},
                "role": "user",
                "content": {
                    "content_type": "text",
                    "parts": [f"{initial_message}"]
                }
            }
        ],
        "parent_message_id": f"{uuid_01}",
        "model": "text-davinci-002-render-sha"
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    # Busca la variable "conversation_id" dentro del stream de datos y llama a la función "conversation_id_callback" con su valor
    for line in response.iter_lines():
        if line:
            try:
                text_str = line.decode('utf-8')
                datos = json.loads(text_str.split("data: ")[1])
                if 'conversation_id' in datos and not entered:
                    entered = True
                    conversation_id = datos['conversation_id']
                    conversation_id_callback(conversation_id, user_id)
            except:
                pass
            callback(line)



def gpt_response(conversation_id, parent_message_id, message, callback):

    url = base_url + f"conversation"
    data = {
        "action": "next",
        "messages": [
            {"author":
             {"role": "user"},
                "role": "user",
                "content":
             {"content_type": "text", "parts":
                 [f"{message}"]
              }
             }
        ],
        "conversation_id": f"{conversation_id}",
        "parent_message_id": f"{parent_message_id}",
        "model": "text-davinci-002-render-sha"
    }
    response = requests.post(url, headers=headers, json=data, stream=True)

    # Llamar a la función de devolución de llamada con cada línea recibida
    for line in response.iter_lines():
        if line:
            callback(line)

def gpt_delete_conversation(conversation_id):
    url = base_url + f"conversation/{conversation_id}"
    data = {
        "is_visible": "false"
    }
    response = requests.patch(url, headers=headers, json=data)
    return response.json()


def gpt_change_title(conversation_id, title):
    url = base_url + f"conversation/{conversation_id}"
    data = {
        "title": f"{title}"
    }
    response = requests.patch(url, headers=headers, json=data)
    return response.json()
