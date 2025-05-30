from spam_filter import is_spam
from secure import des_encrypt, des_decrypt

import socket
import threading
import uuid
import time

PEER_ID = str(uuid.uuid4())[:8]
processed_messages = set() 

def get_user_info():
    username = input("Enter your username: ").strip()
    while not username:
        print("Username cannot be empty!")
        username = input("Enter your username: ").strip()
    return username

username = get_user_info()
HOST = input("Enter your IP: ").strip()
PORT = int(input("Enter your port: "))

KEY = "mysecret"

peers = []
lock = threading.Lock()



def handle_client(conn):
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            decrypted = des_decrypt(data, KEY)
            message_id, sender_id, sender_username, actual_msg = decrypted.split(":", 3)

            if message_id in processed_messages or sender_id == PEER_ID:
                continue

            processed_messages.add(message_id)
            print(f"\n[RECEIVED from {sender_username}]: {actual_msg}\nEnter message: ", end='', flush=True)
        except Exception as e:
            print(f"[ERROR] Connection lost: {e}")
            break




def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"[CONNECTED] Peer connected: {addr}")
        with lock:
            peers.append(conn)
        threading.Thread(target=handle_client, args=(conn,)).start()

def connect_to_peer(peer_host, peer_port):
    try:
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer.connect((peer_host, peer_port))
        with lock:
            peers.append(peer)
        threading.Thread(target=handle_client, args=(peer,)).start()
    except Exception as e:
        print(f"[ERROR] Could not connect to peer: {e}")

def send_messages():
    while True:
        msg = input("Enter message: ")
        if is_spam(msg):
            print("[SPAM DETECTED] Message blocked.")
            continue
            
        message_id = str(int(time.time() * 1000))  # Generate unique message ID
        full_msg = f"{message_id}:{PEER_ID}:{username}:{msg}"
        encrypted = des_encrypt(full_msg, KEY)
        
        with lock:
            for peer in peers:
                try:
                    peer.send(encrypted.encode())
                except:
                    print("[ERROR] Failed to send message.")



if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()

    while True:
        choice = input("Connect to a  peer? (yes/no): ").lower().strip()
        if choice == 'no':
            break
        ip = input("Enter peer IP: ").strip()
        port = int(input("Enter peer Port: "))
        connect_to_peer(ip, port)

    send_messages()