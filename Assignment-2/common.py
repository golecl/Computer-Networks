import socket
import sys
import multiprocessing

bufferSize = 65507

def initialiseSockets(arguments, listStart):
    ipAddresses = []
    for argument in range(listStart, len(arguments)):
        ipAddresses.append(arguments[argument])
        localPort = 54321
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