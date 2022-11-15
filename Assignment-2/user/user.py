# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

id = bytes.fromhex(sys.argv[1])
destinationId = bytes.fromhex(sys.argv[2])
controllerAddress = []
forwarderAddressPort = (sys.argv[3], 54321)
controllerAddress.append(sys.argv[4])
sockets = initialiseSockets(sys.argv, 5)  

time.sleep(4)
for sock in sockets:
    declare(sock, controllerAddress, id)
time.sleep(1)


print("User {} is attempting to send".format(id.hex().upper()))

header = id + destinationId
message = " User with id {} sent this!".format(id)
bytesMessage = str.encode(message)
bytesMessage = header + bytesMessage
sockets[0].sendto(bytesMessage, forwarderAddressPort)

while True:
    receivedBytes = sockets[0].recvfrom(bufferSize)
    message = receivedBytes[0]
    if id == getFinalId(message):
        print("Received this message from user {}:".format(message[0:3].hex().upper()), message)



