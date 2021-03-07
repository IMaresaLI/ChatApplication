import socket
from threading import Thread

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1881 
separator_token = "<<MPRM>>" 
client_sockets = set()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs):
    while True:
        try:
            msg = cs.recv(1024).decode("UTF-8")
            print(msg)
        except Exception as Err :
            print("Bağlantı Kapatıldı")
            client_sockets.remove(cs)
        except ConnectionResetError:
            print("Bağlantı Kapatıldı.")
            client_sockets.remove(cs)
        else:
            msg = msg.replace(separator_token, ": ")
        for client_socket in client_sockets:
            client_socket.send(msg.encode())

while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    client_sockets.add(client_socket)
    t = Thread(target=listen_for_client, args=(client_socket,))
    t.daemon = True
    t.start()



for cs in client_sockets:
    cs.close()
with open("tt.txt","w") as file :
    file.write("Açık")
s.close() 