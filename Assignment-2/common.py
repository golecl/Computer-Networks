import socket
import sys
import multiprocessing

bufferSize = 65507

def initialiseSockets(arguments, listStart):
    ipAddresses = []
    for argument in range(listStart, len(arguments)):
        ipAddresses.append(arguments[argument])
    sockets = []
    # creates the sockets necessary
    for ip in ipAddresses:
        UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPSocket.bind((ip, 54321))
        sockets.append(UDPSocket)
    return sockets

def compareSubnet(ipAddress1, ipAddress2):
    ipAddress1Split = ipAddress1.split(".", 2)
    subnet1 = ipAddress1Split[0] + "." + ipAddress1Split[1]
    ipAddress2Split = ipAddress2.split(".", 2)
    subnet2 = ipAddress2Split[0] + "." + ipAddress2Split[1]
    return subnet1 == subnet2

def getControllerAddress(ownIp, controllerAddress):
    for address in controllerAddress:
        if compareSubnet(ownIp, address):
            controllerSocket = (address, 54321)
    return controllerSocket
        
def declare(sock, controllerAddress, id):
    declaration = id
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp, controllerAddress)
    sock.sendto(declaration, controllerSocket)
    
# returns the final destination id in bytes
def getFinalId(bytesMessage):
    finalId = bytesMessage[3:7]
    return finalId