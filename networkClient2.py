import selectors
import socket

socketManager = selectors.DefaultSelector()

def read(sock):
    msg = sock.recv(1)
    print(msg.decode())

s = socket.socket()

myPort = 1236
myHost = socket.gethostname()
myAddr = (myHost, myPort)

targetAddr = (socket.gethostname(), 1234)

s.bind(myAddr)
s.connect(targetAddr)
s.setblocking(False)
socketManager.register(s, selectors.EVENT_READ, read)

while True:
    msg = input("Enter text: ")
    s.send(msg.encode("UTF8"))
    if(msg == b"q"):
        break
    events = socketManager.select(timeout=None)
    for (key, mask) in events:
        toCall = key.data
        read(key.fileobj)

socketManager.unregister(s)
s.close()
