# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

id = bytes.fromhex(sys.argv[1])
destinationId = bytes.fromhex(sys.argv[2])
controllerAddress = []
forwarderAddressPort = (sys.argv[3], 54321)
controllerAddress.append(sys.argv[4])
sockets = initialiseSockets(sys.argv, 5)  
    
for sock in sockets:
    declare(sock, controllerAddress, id)



print("User is attempting to send")

header = id + destinationId
message = "User with id {} sent this!".format(id)
bytesMessage = str.encode(message)
bytesMessage = header + bytesMessage
sockets[0].sendto(bytesMessage, forwarderAddressPort)

#msgFromForwarder = sockets[0].recvfrom(bufferSize)
#forwarderConfirmation = msgFromForwarder[0]
#print("Forwarder Message: {}".format(forwarderConfirmation))

while True:
    receivedBytes = sockets[0].recvfrom(bufferSize)
    message = receivedBytes[0]
    if id == getFinalId(message):
        print("Woo! received the message!!", message)



