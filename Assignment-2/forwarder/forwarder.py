# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2
from common import *

id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
controllerAddress.append(sys.argv[3])
sockets = initialiseSockets(sys.argv, 4)
        
def getControllerAddress(ownIp):
    for address in controllerAddress:
        if compareSubnet(ownIp, address):
            controllerSocket = (address, 54321)
    return controllerSocket
        
def declare(sock):
    declaration = id
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp)
    sock.sendto(declaration, controllerSocket)

# returns the final destination id in bytes
def getFinalId(bytesMessage):
    finalId = bytesMessage[3:7]
    return finalId

# sends the forwarders id and the final destination id to the controller
# controller sends back the next ip address
def getForwardingAddress(sock, bytesMessage):
    finalId = getFinalId(bytesMessage)
    header = id + finalId
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp)
    sock.sendto(header, controllerSocket)
    nextAddress = sock.recvfrom(bufferSize)
    return nextAddress


def listenAndForward(sock):
    #print(sock)
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
for sock in sockets:
    declare(sock)
    process = multiprocessing.Process(target=listenAndForward,args=[sock])
    process.start()
