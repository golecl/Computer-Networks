# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
sockets = initialiseSockets(sys.argv, 3)  
time.sleep(3.5)
    
for sock in sockets:
    declare(sock, controllerAddress, id)

print("UDP Endpoint up and listening")

while True:
    msgAddressPair = sockets[0].recvfrom(bufferSize)
    receivedMessage = msgAddressPair[0]
    address = msgAddressPair[1]
    
    message = "The user {} sent this: {}".format(receivedMessage[0:3].hex().upper(), receivedMessage)
    
    print(message)