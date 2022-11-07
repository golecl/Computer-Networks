# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

import socket

localIP = "172.30.16.4"
localPort = 54321
UDPEndpointSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPEndpointSocket.bind((localIP, localPort))

bufferSize = 65507

print("UDP Endpoint up and listening")

while True:
    msgAddressPair = UDPEndpointSocket.recvfrom(bufferSize)
    receivedMessage = msgAddressPair[0]
    address = msgAddressPair[1]
    
    message = "The user sent this: {}".format(receivedMessage)
    
    print(message)