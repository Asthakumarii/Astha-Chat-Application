import hashlib
import socket
import threading
from datetime import datetime
import os
from cryptography.fernet import Fernet

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):

    try:
        with open("users.txt", "r") as file:
            for line in file:
                user, pwd = line.strip().split(",")

                if user == username and pwd == hash_password(password):
                    return True
        return False

    except Exception as e:
        print("ERROR:", e)
        return False
# Lists and dictionaries to keep track of connected clients and their nicknames
clients = []
nicknames = {}  # Stores client socket as key and nickname as value
rooms = {
    "General": [],
    "Python": [],
    "Placement": []
}

# Function to handle incoming messages from each individual client
def handle_client(client_socket, client_address):
    try:
        # First step: Receive the nickname immediately after connection
        login_data = client_socket.recv(1024).decode('utf-8')

        try:
            username, password = login_data.split(",", 1)

            username = username.strip()
            password = password.strip()

        except ValueError:
            client_socket.send("AUTH_FAILED".encode('utf-8'))
            client_socket.close()
            return

        if not authenticate(username, password):
            client_socket.send("AUTH_FAILED".encode('utf-8'))
            client_socket.close()
            return

        client_socket.send("AUTH_SUCCESS".encode('utf-8'))
        nickname = username
        nicknames[client_socket] = nickname
        clients.append(client_socket)
        room_name = client_socket.recv(1024).decode('utf-8')

        if room_name not in rooms:
            room_name = "General"

        rooms[room_name].append(client_socket)

        print(f"[NEW CONNECTION] {client_address} is now connected as '{nickname}'.")
        
        # Broadcast to everyone that a new user has joined the room
        join_msg = f"[SYSTEM] {nickname} joined {room_name} room!"
        save_message(join_msg)
        broadcast(join_msg, client_socket)
        send_online_users()

        while True:
            # Continuously listen for incoming messages from the client
            encrypted_message = client_socket.recv(1024)
            print("ENCRYPTED:", encrypted_message)

            message = cipher.decrypt(encrypted_message).decode('utf-8')
            print("DECRYPTED:", message)

            if not message:
                break

            if message.startswith("FILE:"):
                filename = message[5:]

                file_data = client_socket.recv(1024 * 1024)

                filepath = os.path.join(
                    "shared_files",
                    filename
                )

                with open(filepath, "wb") as file:
                    file.write(file_data)

                file_msg = (
                    f"[SYSTEM] {nickname} shared file: {filename}"
                )

                save_message(file_msg)

                room_broadcast(file_msg, client_socket, room_name)

                print(file_msg)

                continue
            
            # Print the log on the server terminal
            print(f"[{nickname}]: {message}")
            
            # Forward the message to all other connected clients
            current_time = datetime.now().strftime("%I:%M %p")
            if message.startswith("/dm "):
                parts = message.split(" ", 2)

                if len(parts) == 3:
                    receiver = parts[1]
                    dm_message = parts[2]

                    success = private_message(
                        nickname,
                        receiver,
                        dm_message
                    )

                    if not success:
                        client_socket.send(
                            f"[SYSTEM] User '{receiver}' not found.".encode('utf-8')
                        )

            else:
                formatted_message = f"[{current_time}] [{nickname}]: {message}"
                save_message(formatted_message)
                room_broadcast(formatted_message, client_socket, room_name)
            
    except:
        pass
    finally:
        # Cleanup routine when a client disconnects
        if client_socket in nicknames:
            nickname = nicknames[client_socket]
            print(f"[DISCONNECTED] {nickname} ({client_address}) has disconnected.")
            leave_msg = f"[SYSTEM] {nickname} has left the chat room."
            save_message(leave_msg)
            if room_name in rooms:
                room_broadcast(leave_msg, client_socket, room_name)
            del nicknames[client_socket]
            send_online_users()
            
        if client_socket in clients:
            clients.remove(client_socket)

        if room_name in rooms:
            if client_socket in rooms[room_name]:
                rooms[room_name].remove(client_socket)
            
        client_socket.close()

def save_message(message):
    with open("chat_history.txt", "a", encoding="utf-8") as file:
        file.write(message + "\n")

# Function to broadcast messages to all clients except the sender
def broadcast(message, current_client):
    for client in clients:
        if client != current_client:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                if client in clients:
                    clients.remove(client)
                if client in nicknames:
                    del nicknames[client]

def room_broadcast(message, current_client, room_name):
    
     for client in rooms[room_name]:
        if client != current_client:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print("SEND ERROR:", e)
                pass

def private_message(sender, receiver_name, message):
    for client, nickname in nicknames.items():
        if nickname == receiver_name:
            try:
                client.send(
                    f"[PRIVATE] [{sender}]: {message}".encode('utf-8')
                )
                return True
            except:
                return False
    return False

def send_online_users():
    users = ", ".join(nicknames.values())

    message = f"[SYSTEM] Online Users: {users}"

    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            pass

def create_files_folder():
    if not os.path.exists("shared_files"):
        os.makedirs("shared_files")

with open("secret.key", "rb") as file:
    key = file.read()

cipher = Fernet(key)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5000))
    server.listen()
    create_files_folder()
    print("[STARTING] Server is up and running on port 5000...")

    while True:
        client_socket, client_address = server.accept()
        
        # Start a dedicated background thread for every new connection
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_server()