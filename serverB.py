import socket

def start_server():
    # 1. सॉकेट ऑब्जेक्ट बनाएं (IPv4, TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. IP और Port नंबर सेट करें (Localhost के लिए 127.0.0.1)
    host = '127.0.0.1'
    port = 5000
    
    # 3. सर्वर को होस्ट और पोर्ट से बाइंड करें
    server.bind((host, port))
    
    # 4. कनेक्शन के लिए सुनना (Listen) शुरू करें
    server.listen(1)
    print(f"Server चालू है और port {port} पर कनेक्शन का इंतजार कर रहा है...")
    
    # 5. क्लाइंट का कनेक्शन स्वीकार करें
    conn, addr = server.accept()
    print(f"क्लाइंट {addr} से कनेक्शन जुड़ गया है!")
    
    # 6. चैट लूप (लगातार मैसेज एक्सचेंज करने के लिए)
    while True:
        # क्लाइंट का मैसेज रिसीव करें (अधिकतम 1024 बाइट्स)
        client_message = conn.recv(1024).decode('utf-8')
        if not client_message or client_message.lower() == 'bye':
            print("क्लाइंट ने चैट बंद कर दी।")
            break
        print(f"Client: {client_message}")
        
        # अपना रिप्लाई भेजें
        server_reply = input("You (Server): ")
        conn.send(server_reply.encode('utf-8'))
        if server_reply.lower() == 'bye':
            break
            
    conn.close()
    server.close()

if __name__ == "__main__":
    start_server()