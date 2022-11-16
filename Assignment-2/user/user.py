# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

# This initial block of code initialies all variables and sockets
# It gets all of the IP information from the arguments passed into it
id = bytes.fromhex(sys.argv[1])
destinationId = bytes.fromhex(sys.argv[2])
controllerAddress = []
forwarderAddressPort = (sys.argv[3], 54321)
controllerAddress.append(sys.argv[4])
sockets = initialiseSockets(sys.argv, 5)  

# This declares the socket of the user to the controller
# The timeouts are necessary as the controller takes some time to initialise all of its sockets etc.
# Without the timeout, the program often fails due to multiprocessing complexity
time.sleep(4)
for sock in sockets:
    declare(sock, controllerAddress, id)
time.sleep(1)


print("User {} is attempting to send a message".format(id.hex().upper()))

# The user creates a header which is its own Element ID followed by the Destinations Element ID
# It then concatenates this with the message it wants to send
# It then sends it to the gateway/forwarder in its network
header = id + destinationId
message = " User with id {} sent this!".format(id)
bytesMessage = str.encode(message)
bytesMessage = header + bytesMessage
sockets[0].sendto(bytesMessage, forwarderAddressPort)

# This while loop awaits any messages sent to its socket, it enables other users to send
# Messages to other users
while True:
    receivedBytes = sockets[0].recvfrom(bufferSize)
    message = receivedBytes[0]
    if id == getFinalId(message):
        print("Received this message from user {}:".format(message[0:3].hex().upper()), message)



