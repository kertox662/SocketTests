import socket
import threading
import logging
import atexit

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def closeSocket():
    print("Starting to close connections")
    global s, connections
    for c in connections:
        try:
            c.close()
        except Exception:
            pass
    s.close()
    print("Finished closing connections")

atexit.register(closeSocket)

host = ""
port = 4545

connections = []
names = ["Users:"]

print("Socket Created")

s.bind((host, port))

print("Socket Bound")

s.listen(5)

print("Socket is Listening")


def clientHandler(conn,addr):
    print("Connected with client.\nIP:{}, Port:{}".format(addr[0], addr[1]))
    while True:
        data = conn.recv(2048)
        if not data:
            break
        try:
            data = data.decode('utf-8')#.split("\n")
        except:
            break
        print(data)
        if data.startswith("|User|"):
            global names
            username = data.split("|User|")[1]
            print(username)
            names.append(username)
            data = "|Users|{}".format(names)
        #data.pop(-1)
        #data = data[0]

        #data = "Server Message: {}\n".format(data)
        
        for c in connections:
            c.sendall(data.encode())
    
    conn.close()
    print("Disconnected from client.\nIP:{}, Port:{}".format(addr[0], addr[1]))
    names.remove(username)
    for c in connections:
        c.sendall("{} has disconnected".format(username).encode())
        c.sendall("|Users|{}".format(names).encode())


while True:
    conn, addr = s.accept()
    connections.append(conn)
    thread = threading.Thread(target = clientHandler, args=(conn, addr))
    thread.start()
