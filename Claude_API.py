import requests
import json
import os
import uuid

uuid_organization = ''
uuid_conversation = ''
cookie = ''
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 OPR/99.0.0.0'
#------------------------------------------------------------------------------
def load_cookie():
    global cookie
    with open(f'{os.getcwd()}/claude.json', "r", encoding="utf-8") as file:
        data = json.load(file)
        if isinstance(data, list):
            for item in data:
                if item.get("name") == "sessionKey":
                    cookie = item.get("value")
#------------------------------------------------------------------------------
def generate_uuid():
    random_uuid = uuid.uuid4()
    random_uuid_str = str(random_uuid)
    formatted_uuid = f"{random_uuid_str[0:8]}-{random_uuid_str[9:13]}-{random_uuid_str[14:18]}-{random_uuid_str[19:23]}-{random_uuid_str[24:]}"
    return formatted_uuid
#------------------------------------------------------------------------------
def create_new_chat():
    global uuid_organization
    global cookie
    global user_agent

    url = f"https://claude.ai/api/organizations/{uuid_organization}/chat_conversations"

    payload = json.dumps({"uuid": generate_uuid(), "name": ""})
    headers = {
      'User-Agent': f'{user_agent}',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Origin': 'https://claude.ai',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Cookie': f'sessionKey={cookie}',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'TE': 'trailers'
    }

    requests.request("POST", url, headers=headers, data=payload)
#------------------------------------------------------------------------------
def get_organization_id():
    global uuid_organization
    global cookie
    global user_agent

    url = "https://claude.ai/api/organizations"

    headers = {
        "sec-ch-ua": '"Opera";v="99", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-platform": '"Windows"',
        "Referer": "https://claude.ai/chat/0a916e50-47af-4d2e-b424-681e59a720d7",
        "DNT": "1",
        "sec-ch-ua-mobile": "?0",
        'User-Agent': f'{user_agent}',
        "Content-Type": "application/json",
        "Cookie": f"sessionKey={cookie}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    uuid_organization = data[0]['uuid']
#------------------------------------------------------------------------------
def list_conversation():
    global uuid_organization
    global uuid_conversation
    global cookie
    global user_agent

    url = f"https://claude.ai/api/organizations/{uuid_organization}/chat_conversations"

    headers = {
      'User-Agent': f'{user_agent}',
      "Content-Type": "application/json",
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://claude.ai/chats',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      "Cookie": f"sessionKey={cookie}"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        uuid_conversation = data[0]['uuid']
    except Exception as e:
        create_new_chat()
        list_conversation()
#------------------------------------------------------------------------------
# Send Message to Claude
def send_message(prompt):
    global uuid_organization
    global uuid_conversation
    global cookie    
    global user_agent

    if uuid_organization == '' or uuid_conversation == '':
       get_organization_id()
       list_conversation()

    url = "https://claude.ai/api/append_message"

    payload = json.dumps({
      "completion": {
        "prompt": f"{prompt}",
        "timezone": "America/Sao_Paulo",
        "model": "claude-2"
      },
      "organization_uuid": f"{uuid_organization}",
      "conversation_uuid": f"{uuid_conversation}",
      "text": f"{prompt}",
      "attachments": []
    })
    headers = {
      'User-Agent': f'{user_agent}',
      'Accept': 'text/event-stream, text/event-stream',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Referer': 'https://claude.ai/chats',
      'Content-Type': 'application/json',
      'Origin': 'https://claude.ai',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Cookie': f'sessionKey={cookie}',
      'Sec-Fetch-Dest': 'empty',
      "sec-ch-ua-platform": "Windows",
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'TE': 'trailers'
    }

    response = requests.post(url, headers=headers, data=payload, stream=True)
    data = response.text.strip().split('\n')[-1]
    # Ajuste da codificação
    data = data.encode('latin1').decode('utf-8')
    answer = json.loads(data[6:])['completion']
    return {"answer": json.loads(data[6:])['completion']}['answer']
#------------------------------------------------------------------------------
  # Deletes the conversation
def delete_conversation():
    global uuid_organization
    global uuid_conversation
    global cookie    
    global user_agent

    url = f"https://claude.ai/api/organizations/{uuid_organization}/chat_conversations/{uuid_conversation}"

    payload = json.dumps(f"{uuid_conversation}")
    headers = {
      'User-Agent': f'{user_agent}',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Content-Type': 'application/json',
      'Content-Length': '38',
      'Referer': 'https://claude.ai/chats',
      'Origin': 'https://claude.ai',
      "sec-ch-ua": 'Opera/99, Chromium/113, Not-A.Brand/24',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'dnt': '1',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Cookie': f'sessionKey={cookie}',
      'TE': 'trailers'
    }
    requests.request("DELETE", url, headers=headers, data=payload)
#------------------------------------------------------------------------------
load_cookie()
print(send_message("diferença entre fada e gnomo?"))
delete_conversation()