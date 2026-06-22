import socket

def start_client():
    # 1. सॉकेट ऑब्जेक्ट बनाएं
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = '127.0.0.1'
    port = 5000
    
    # 2. सर्वर से कनेक्ट करें
    client.connect((host, port))
    print("सर्वर से कनेक्शन जुड़ गया! अब आप चैट कर सकते हैं।")
    
    # 3. चैट लूप
    while True:
        # सर्वर को मैसेज भेजें
        my_message = input("You (Client): ")
        client.send(my_message.encode('utf-8'))
        if my_message.lower() == 'bye':
            break
            
        # सर्वर का रिप्लाई रिसीv करें
        server_reply = client.recv(1024).decode('utf-8')
        if not server_reply or server_reply.lower() == 'bye':
            print("सर्वर ने चैट बंद कर दी।")
            break
        print(f"Server: {server_reply}")
        
    client.close()

if __name__ == "__main__":
    start_client()