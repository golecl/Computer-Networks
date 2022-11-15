# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2
from common import *

id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
controllerAddress.append(sys.argv[3])
sockets = initialiseSockets(sys.argv, 4)    
time.sleep(3)    

# sends the forwarders id and the final destination id to the controller
# controller sends back the next ip address
def getForwardingAddress(sock, bytesMessage):
    finalId = getFinalId(bytesMessage)
    header = id + finalId
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp, controllerAddress)
    sock.sendto(header, controllerSocket)
    nextAddressBytes = sock.recvfrom(bufferSize)[0]
    nextAddressString = nextAddressBytes.decode()
    nextAddress = (nextAddressString, 54321)
    return nextAddress

def listenAndForward(sock):
    while True:
        receivedBytes = sock.recvfrom(bufferSize)
        message = receivedBytes[0]
        address = receivedBytes[1]
        print("The user {} wants to send this message: {}".format(message[0:3].hex().upper(), message))
        destination = getFinalId(message)
        if id == destination:
            break
        nextAddress = getForwardingAddress(sock, message)
        sock.sendto(message, nextAddress)
        continue
    print("Reached destination!")

print("Forwarder {} is up".format(id.hex().upper()))
for sock in sockets:
    declare(sock, controllerAddress, id)
    process = multiprocessing.Process(target=listenAndForward,args=[sock])
    process.start()
