
import socket
import threading
import json

def handle_client(client_socket, address):
    print(f"[+] New connection from {address}")
    
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            
            # Parse command from phone
            command = data.decode('utf-8')
            print(f"[{address}] {command}")
            
            # Send response
            response = "Command received"
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            print(f"[!] Error: {e}")
            break
    
    client_socket.close()
    print(f"[-] Connection closed: {address}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 4444))
    server.listen(5)
    
    print(f"[*] Listening on port 4444...")
    print(f"[*] Waiting for infected devices to connect...")
    
    while True:
        client, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client, address))
        client_thread.start()

if __name__ == "__main__":
    main()
