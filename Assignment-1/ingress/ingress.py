import socket
import random
from random import randrange

messageCodes = ["r3qu35t-cl13nt","c0nf1rmat10n-cl13nt", "r3qu35t-w0rk3r",
                "c0nf1rmat10n-w0rk3r", "r3qu35t-1ngr355", "c0nf1rmat10n-1ngre55",
                 "d3clarat10n-cl13nt", "d3clarat10n-w0rk3r"]
# code r3qu35t = request
# code c0nf1rmat10n = confirmation
# code d3clarat10n" declaration
# code "cl13nt" = client
# code "w0rk3r" = worker
# code "1ngr355" = ingress

# each message will contain a 36 bit binary number. the first 4 bits will correspond to the codes above,
# used to identify what type of action should be taken
# the next 16 bits will correspond to the client assigned to the action
# the last 16 bits will be used to identified to the worker tied to the action
# as to reserve the ability to have no worker and/or no client assigned
# the bits "0000000000000000" will be assigned to an empty worker/client
# this means that the binary number is +1 whatever index the worker or client is

# POSSIBLE FEATURE IF I HAVE TIME:
# the udp packet size limit is 65507 bytes. this can be worked around by splitting a file up into multiple
# parts on the client side and then including a couple bits in the binary message at the start which would
# indicate how many parts of the file there are and which part of the file is included in the datagram.
# this would take extra methods on the ingress and client side along with a change to the binary code
# system in all classes. it would probably not be too difficult but it is also not necessary

#TODO
# change all messages into just containing the binary header and the file we need to transfer
# change the "createBinaryCode" function so that it doesnt add "[]" and change the other functions approrpriately
# possibly implement the method described above

localIP = "127.0.0.1"
localPort = 49668
bufferSize = 1024
clientAddresses = []
workerAddresses = []
currentClient = -1
currentWorker = -1
clientWorkerBits = 16
codeBits = 4

# function used to find worker addresses or add them if they do not exist on the list yet
def findIfUnitAlreadyDeclared(list, address):
    # if the unit is already in the list, it returns its index
    try:
        index = list.index(address)
        return index
    # if it is not already on the list it adds it to the end and returns its index
    except:
        list.append(address)
        return list.index(address)

# creates the binary code used to identify the action, client, and worker
# returns it in [] and with client and worker numbers incremented by 1
def createBinaryCode(messageCode, client, worker):
    msgCodeBin = f'{messageCode:0{codeBits}b}' # creates a 4 bit binary number of the message code
    client+=1
    clientBin = f'{client:0{clientWorkerBits}b}' # creates a 16 bit binary number of the client number
    worker+=1
    workerBin = f'{worker:0{clientWorkerBits}b}'# creates a 16 bit binary number of the client number
    binaryCode = "[" + msgCodeBin + clientBin + workerBin + "]"
    return binaryCode

# gets the binary code from a string message
# CURRENTLY SET UP TO WORK WITH THE SYSTEM OF THE [] ENCASING THE BINARY CODE
# IF THIS SYSTEM CHANGES YOU HAVE TO CHANGE THE CODE OF THIS FUNCTION AND COPY AND PASTE IT TO THE WORKER AND CLIENT
def getBinaryCodeFromMessage(message):
    # ONCE THE BINARY CODE IS THE ONLY THING IN THE MESSAGE THEN REPLACE THE LINE WITH
    # binaryCode = message[len(message) - (codeBits + 2*clientWorkerBits): len(message) - 1]
    binaryCode = message[len(message) - (codeBits + 2*clientWorkerBits + 1): len(message) - 1]
    return binaryCode

# returns a list of the code, client, and worker contained in a binary string
def findCodeClientWorker(binaryString):
    msgCode = int(binaryString[0:codeBits], 2) # gets the message code from the string
    clientNum = int(binaryString[codeBits:codeBits + clientWorkerBits], 2) - 1 # gets the client number from the string
    workerNum = int(binaryString[codeBits + clientWorkerBits:codeBits + clientWorkerBits + clientWorkerBits], 2) - 1 # gets the worker number from the string
    values = [msgCode, clientNum, workerNum]
    return values

# gets the message code from a binary string
def findCode(binaryString):
    return findCodeClientWorker(binaryString)[0]

# gets the client number from a binary string
def findClient(binaryString):
    return findCodeClientWorker(binaryString)[1]

# gets the worker number from a binary string
def findWorker(binaryString):
    return findCodeClientWorker(binaryString)[2]

# create a datagram socket
UDPIngressSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# bind to address and ip
UDPIngressSocket.bind((localIP, localPort))

print("UDP ingress up and listening")

# listen for incoming datagrams
while True:
    # constantly trying to receive messages
    bytesAddressPair = UDPIngressSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    stringMessage = message.decode();
    binaryCode = getBinaryCodeFromMessage(stringMessage)
    receivedMessageCode = findCode(binaryCode)

    # if a worker sends a delcaration of existence
    if receivedMessageCode == 7:
        # gets the index of the current workers address
        currentWorker = findIfUnitAlreadyDeclared(workerAddresses, address)
        confirmation = "Yes, worker I see you! [Code: {}] {}".format(messageCodes[5], createBinaryCode(5, -1, currentWorker))
        print(confirmation)
        bytesToSend = str.encode(confirmation)
        UDPIngressSocket.sendto(bytesToSend, workerAddresses[currentWorker])

    # if a client sends a delcaration of existence
    if receivedMessageCode == 6:
        currentClient = findIfUnitAlreadyDeclared(clientAddresses, address)
        confirmation = "Yes, client I see you! [Code: {}] {}".format(messageCodes[5], createBinaryCode(5, currentClient, -1))
        print(confirmation)
        bytesToSend = str.encode(confirmation)
        UDPIngressSocket.sendto(bytesToSend, clientAddresses[currentClient])

    # if a client sends a request
    if receivedMessageCode == 0:
        # the client message gets recorded and sorted into the appropriate variables
        currentClient = findIfUnitAlreadyDeclared(clientAddresses, address)
        # if workers have declared themselves, the ingress will choose a random one and send on the clients request to them
        if len(workerAddresses) != 0:
            currentWorker = randrange(len(workerAddresses))
            requestToWorker = "Hi hello i received a request from client, passing it on, okay bye [Code: {}] {}".format(messageCodes[4], createBinaryCode(4, currentClient, currentWorker))
            print(requestToWorker)
            bytesToSend = str.encode(requestToWorker)
            UDPIngressSocket.sendto(bytesToSend, workerAddresses[currentWorker])

    # if a worker sends confirmation
    if receivedMessageCode == 3:
        currentClient = findClient(binaryCode)
        currentWorker = findWorker(binaryCode)
        stringMessage = "WORKER RECEIVEDDDDDDDDDD gut job :3 [Code: {}] {}".format(messageCodes[5], createBinaryCode(5, currentClient, currentWorker))
        print(stringMessage)
        bytesToSend = str.encode(stringMessage)
        UDPIngressSocket.sendto(bytesToSend, clientAddresses[currentClient])
