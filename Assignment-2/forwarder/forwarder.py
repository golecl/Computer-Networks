# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

# This initial block of code initialies all variables and sockets
# It gets all of the IP information from the arguments passed into it
id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
controllerAddress.append(sys.argv[3])
sockets = initialiseSockets(sys.argv, 4)    
time.sleep(3)    

# Sends the forwarders Element ID and the final destination ID to the controller
# Controller sends back the next IP address
def getForwardingAddress(sock, bytesMessage):
    try:
        finalId = getFinalId(bytesMessage)
        header = id + finalId
        currentIp = sock.getsockname()[0]
        controllerSocket = getControllerAddress(currentIp, controllerAddress)
        sock.sendto(header, controllerSocket)
        nextAddressBytes = sock.recvfrom(bufferSize)[0]
        nextAddressString = nextAddressBytes.decode()
        nextAddress = (nextAddressString, 54321)
        return nextAddress
    except:
        print("Sorry, error was encountered in the forwarder. Please try again.")

# This function continuously waits for a message, it then asks the controller where it should
# Send it to. It then sends it to that address from the appropriate socket. (It uses the compareSubnets
# function to determine which socket it should send it to)
def listenAndForward(sock):
    try:
        while True:
            receivedBytes = sock.recvfrom(bufferSize)
            message = receivedBytes[0]
            print("The user {} wants to send this message: {}".format(message[0:3].hex().upper(), message))
            nextAddress = getForwardingAddress(sock, message)
            sock.sendto(message, nextAddress)
    except:
        print("")

print("Forwarder {} is up".format(id.hex().upper()))

# This for loop declares all of the forwarders sockets and creates a process for each of them so they can both
# Run at the same time, it throws an error if one is caught.
for sock in sockets:
    try:
        declare(sock, controllerAddress, id)
        process = multiprocessing.Process(target=listenAndForward,args=[sock])
        process.start()
    except:
        print("Sorry, an error occurred in the forwarder {}. Please restart and try again.".format(id))
        continue
