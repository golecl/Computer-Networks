# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

# This initial block of code initialies all variables and sockets
# It gets all of the IP information from the arguments passed into it
id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
sockets = initialiseSockets(sys.argv, 3)  

# This declares the socket of the user to the controller
# The timeouts are necessary as the controller takes some time to initialise all of its sockets etc.
# Without the timeout, the program often fails due to multiprocessing complexity
time.sleep(3.5)
for sock in sockets:
    declare(sock, controllerAddress, id)

print("UDP Endpoint up and listening")

# This while loop awaits any messages, it then prints out the message and the user that sent it
while True:
    msgAddressPair = sockets[0].recvfrom(bufferSize)
    receivedMessage = msgAddressPair[0]
    message = "Message received at endpoint! The user {} sent this: {}".format(receivedMessage[0:3].hex().upper(), receivedMessage)
    print(message)