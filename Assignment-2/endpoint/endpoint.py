# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

import socket
from common import *

id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
sockets = initialiseSockets(sys.argv, 3)  
    
for sock in sockets:
    declare(sock, controllerAddress, id)

print("UDP Endpoint up and listening")

while True:
    msgAddressPair = sockets[0].recvfrom(bufferSize)
    receivedMessage = msgAddressPair[0]
    address = msgAddressPair[1]
    
    message = "The user sent this: {}".format(receivedMessage)
    
    print(message)