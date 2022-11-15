# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
sockets = initialiseSockets(sys.argv, 3)  
    
for sock in sockets:
    declare(sock, controllerAddress, id)

forwarderAddressPort = ("192.168.17.34", 54321)

print("User is attempting to send")

header = bytes.fromhex('AAAAAAFFFFFF') 
message = "The user sent this message!"
bytesMessage = str.encode(message)
bytesMessage = header + bytesMessage
sockets[0].sendto(bytesMessage, forwarderAddressPort)

msgFromForwarder = sockets[0].recvfrom(bufferSize)
forwarderConfirmation = msgFromForwarder[0]
print("Forwarder Message: {}".format(forwarderConfirmation))



