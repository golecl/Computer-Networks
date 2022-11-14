# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2
from common import *

id = bytes.fromhex(sys.argv[1])
controllerAddress = (sys.argv[2], 54321)
sockets = initialiseSockets(sys.argv, 3)
        
def declare(sock):
    declaration = id
    sock.sendto(declaration, controllerAddress)

# returns the final destination id in bytes
def getFinalId(bytesMessage):
    finalId = bytesMessage[3:7]
    return finalId

# sends the forwarders id and the final destination id to the controller
# controller sends back the next ip address
def getForwardingAddress(sock, bytesMessage):
    finalId = getFinalId(bytesMessage)
    header = id + finalId
    sock.sendto(header, controllerAddress)
    nextAddress = sock.recvfrom(bufferSize)
    return nextAddress


def listenAndForward(sock):
    print(sock)
    while True:
        receivedBytes = sock.recvfrom(bufferSize)
        message = receivedBytes[0]
        address = receivedBytes[1]
        print("The client wants to send this message: {}".format(message))
        print("The clients ip is: {}".format(address))
        nextAddress = getForwardingAddress(sock, message)
        sock.sendto(message, nextAddress)
        continue

print("Forwarder is up")
print(sockets)
for sock in sockets:
    declare(sock)
    process = multiprocessing.Process(target=listenAndForward,args=[sock])
    process.start()
