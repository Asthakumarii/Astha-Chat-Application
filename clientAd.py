import socket
import threading

# सर्वर से आने वाले मैसेज को लगातार सुनने का फंक्शन
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"\n{message}")
        except:
            print("[ERROR] सर्वर से कनेक्शन टूट गया।")
            client_socket.close()
            break

# सर्वर को मैसेज भेजने का फंक्शन
def send_messages(client_socket):
    while True:
        try:
            message = input()
            if message.lower() == 'bye':
                client_socket.close()
                break
            client_socket.send(message.encode('utf-8'))
        except:
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5000))
    
    # --- नाम इनपुट लेने का मजबूत सिस्टम ---
    while True:
        nickname = input("चैट में शामिल होने के लिए अपना नाम डालें: ").strip()
        
        if not nickname:
           
            print("[ALERT] नाम खाली नहीं हो सकता! कृपया दोबारा डालें।")
            continue
        else:
            break
            
    client.send(nickname.encode('utf-8'))
    print(f"[CONNECTED] आप '{nickname}' के रूप में जुड़ चुके हैं। टाइप करना शुरू करें:\n")

    # मैसेज रिसीव करने के लिए अलग थ्रेड
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # मैसेज भेजने के लिए मेन थ्रेड काम करेगा
    send_messages(client)

if __name__ == "__main__":
    start_client()