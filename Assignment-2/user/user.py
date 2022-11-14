# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

import socket

localIP = ""
localPort = 54321
UDPUserSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPUserSocket.bind((localIP, localPort))

bufferSize = 65507

forwarderAddressPort = ("192.168.17.34", 54321)

print("User is attempting to send")

message = "The user sent this message!"
bytesMessage = str.encode(message)
UDPUserSocket.sendto(bytesMessage, forwarderAddressPort)

msgFromForwarder = UDPUserSocket.recvfrom(bufferSize)
forwarderConfirmation = msgFromForwarder[0]
print("Forwarder Message: {}".format(forwarderConfirmation))



