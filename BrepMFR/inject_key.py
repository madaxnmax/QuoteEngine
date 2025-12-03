import websocket
import json
import uuid
import ssl
import sys

# Configuration
BASE_URL = "89a9f3dcea0144feb14f6ccdd40f5d08-0.lambdaspaces.com"
TOKEN = "df13d606b6e54cf2b84b8991cd2d1b8e"
PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCi6bzzFZTpNrDJdw2ITOpbIAGuWBUVr436jhYKdPzQPKG1nAr3+xN9t+9jqC+uSje0/1mUNhmiklV8RQBiAW+8lvEyROFhG8Dv8+0OZZ1B8w9+nZrF7mbQ0KWZCHEpfCOHuXn9mLM5lsS6YPVCJvtwfzG6QCU/m9ttps56Tr4c73la5VTyt/iYbtAxr1QdIwjjI1XXP5jE+zh/WEiMdJ4uULXI24/xUzn70M+OfhbHJ24vVXE0x2U0HmYXmDFS/hAm6xdhPLEfDmKqaEEg9ir0TXMi5t/lW56+NPmPoUZ9M+Y6xmHW1+XZJpvyJv5ooN8Memm/gmhGu0+sb5BMK8OT"

def create_kernel():
    import http.client
    conn = http.client.HTTPSConnection(BASE_URL)
    headers = {"Authorization": f"token {TOKEN}"}
    conn.request("POST", "/api/kernels", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data)["id"]

def execute_code(kernel_id, code):
    ws_url = f"wss://{BASE_URL}/api/kernels/{kernel_id}/channels?token={TOKEN}"
    ws = websocket.create_connection(ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
    
    msg_id = str(uuid.uuid4())
    msg = {
        "header": {
            "msg_id": msg_id,
            "username": "username",
            "session": str(uuid.uuid4()),
            "msg_type": "execute_request",
            "version": "5.0"
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False
        }
    }
    
    ws.send(json.dumps(msg))
    
    while True:
        res = json.loads(ws.recv())
        msg_type = res["msg_type"]
        if msg_type == "stream":
            print(res["content"]["text"], end="")
        elif msg_type == "execute_reply":
            break
    
    ws.close()

try:
    print("Creating kernel...")
    kernel_id = create_kernel()
    print(f"Kernel created: {kernel_id}")
    
    cmd = f'import os; os.system("echo \'{PUBLIC_KEY}\' >> /home/ubuntu/.ssh/authorized_keys")'
    print(f"Executing: {cmd}")
    execute_code(kernel_id, cmd)
    print("\nKey injected successfully.")
except Exception as e:
    print(f"Error: {e}")
