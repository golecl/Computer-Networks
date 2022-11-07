# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

import socket

localIP = ""
localPort = 54321
UDPForwarderSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPForwarderSocket.bind((localIP, localPort))

bufferSize = 65507

nextAddressPort = ("172.30.16.4", 54321)

print("Forwarder is up")

# wait for messages from users
while True:
    msgAddressPair = UDPForwarderSocket.recvfrom(bufferSize)
    receivedMessage = msgAddressPair[0]
    address = msgAddressPair[1]
    
    message = "The user sent this: {}".format(receivedMessage)
    userIP = "The users address is: {}".format(address)
    UDPForwarderSocket.sendto(receivedMessage, nextAddressPort)
    
    print(message)
    print(userIP)
    
    # send confirmation to the user
    userFeedback = "Message successfully forwarded"
    userFeedback = str.encode(userFeedback)
    UDPForwarderSocket.sendto(userFeedback, address)
