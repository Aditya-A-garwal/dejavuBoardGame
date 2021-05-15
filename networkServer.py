import selectors, socket

class myClient:

    def __init__(self, socket):
        self.sock = socket
        self.msg = b""

    def sendMsg(self):
        self.sock.send(self.msg)
        self.clearMsg()

    def clearMsg(self):
        self.msg = b""

    def fileno(self):
        return self.sock.fileno()


def accept(sock):
    conn, addr = sock.accept()
    print('Accepted connection from', addr)
    conn.setblocking(False)

    clientConn = myClient(conn)
    socketmanager.register(clientConn, selectors.EVENT_READ, read)

def read(client):
    msg = client.sock.recv(2)
    client.msg += msg
    print('recieved', msg.decode(), 'from', client.sock.getpeername())

    if(b";" in msg):
        if(client.msg == b"q;"):
            print('Closing', client.sock.getpeername())
            socketmanager.unregister(client)
            client.sock.close()
        else:
            print('echoing', client.msg.decode(), 'to', client.sock.getpeername())
            client.sendMsg()

socketmanager = selectors.DefaultSelector()

s = socket.socket()
s.bind(('127.0.0.1', 8080))
s.listen()
s.setblocking(False)

socketmanager.register(s, selectors.EVENT_READ, accept)

while True:
    events = socketmanager.select(timeout=None)
    for(key, mask) in events: key.data(key.fileobj)

