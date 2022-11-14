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
