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

# each datagram will contain 7 bytes in the beggining describing all of the useful information
# this information will change but currently it is action code, client number, part number, and total number of parts

# POSSIBLE FEATURE IF I HAVE TIME:
# the udp packet size limit is 65507 bytes. this can be worked around by splitting a file up into multiple
# parts on the client side and then including a couple Bytes in the Byte message at the start which would
# indicate how many parts of the file there are and which part of the file is included in the datagram.
# this would take extra methods on the ingress and client side along with a change to the Byte code
# system in all classes. it would probably not be too difficult but it is also not necessary

#TODO
# CHANGE MESSAGE ENCODING AND DECODING SO IT NEVER DECODES (OR ONLY DECODES IF U WANT STRINGS)
# change all messages into just containing the Byte header and the file we need to transfer
# change the "createByteCode" function so that it doesnt add "[]" and change the other functions approrpriately
# possibly implement the method described above

localIP = "127.0.0.1"
localPort = 49668
bufferSize = 20000
clientAddresses = ['0']
workerAddresses = []
unavailableWorkers = []
currentClient = -1
currentWorker = -1
codeBytes = 1
clientBytes = 2
partNumBytes = 2
fileNameBytes = 2
lastFileBytes = 1
totalHeaderBytes = codeBytes + clientBytes + partNumBytes + fileNameBytes + lastFileBytes

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

# creates the Byte code used to identify the action, client, current file part, and total file parts
def createByteCode(messageCode, client, partNumber, fileNames, lastFile):
    msgCodeByte = messageCode.to_bytes(codeBytes, 'big') # creates a 8 bit Byte number of the message code
    clientByte = client.to_bytes(clientBytes, 'big') # creates a 16 bit Byte number of the client number
    partNum = partNumber.to_bytes(partNumBytes, 'big') # creates a byte sized number
    fileNameNum = fileNames.to_bytes(fileNameBytes, 'big')
    lastFile = lastFile.to_bytes(lastFileBytes, 'big')
    ByteCode = msgCodeByte + clientByte + partNum + fileNameNum + lastFile
    return ByteCode

# gets the Byte code from a string message
# NEEDS TO BE PASSED IN ENCODED AS BYTES OTHERWISE WILL NOT WORK
def getByteCodeFromMessage(message):
    ByteCode = message[0:totalHeaderBytes]
    return ByteCode

# FOR ALL "find" FUNCTIONS BELOW:
    # ONLY PASS IN THE FIRST FEW BYTES OF A MESSAGE BECAUSE OTHERWISE IT MIGHT BE SLOE

# gets the message code from a Byte string in form of int
def findCode(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = 0
    end = start + codeBytes
    return int.from_bytes(message[start:end], 'big')


# gets the client number from a Byte string in form of int
def findClient(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes
    end = start + clientBytes
    return int.from_bytes(message[start:end], 'big')

# gets the part number from a Byte string in form of int
def findPartNum(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes
    end = start + partNumBytes
    return int.from_bytes(message[start:end], 'big')

# gets the total number of parts from a Byte string in form of int
def findfileNameNum(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes
    end = start + fileNameBytes
    return int.from_bytes(message[start:end], 'big')

# gets last file confirmation byte
def findLastFile(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes + fileNameBytes
    end = start + lastFileBytes
    return int.from_bytes(message[start:end], 'big')

def getStringCodeFromByteCode(byteCode):
    code = findCode(byteCode)
    client = findClient(byteCode)
    partNum = findPartNum(byteCode)
    fileNameNum = findfileNameNum(byteCode)
    lastFile = findLastFile(byteCode)
    string = f'{code:0{codeBytes*8}}' + f'{client:0{clientBytes*8}}' + f'{partNum:0{partNumBytes*8}}' + f'{fileNameNum:0{fileNameBytes*8}}' + f'{lastFile:0{lastFileBytes*8}}'
    return string

def selectAvailableWorker():
    currentWorker = workerAddresses.pop(randrange(len(workerAddresses)))
    unavailableWorkers.append(currentWorker)
    return currentWorker

def makeWorkerAvailabe(address):
    currentWorker = unavailableWorkers.pop(findIfUnitAlreadyDeclared(unavailableWorkers, address))
    findIfUnitAlreadyDeclared(workerAddresses, currentWorker)


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

    byteCode = getByteCodeFromMessage(message)

    receivedMessageCode = findCode(byteCode)
    receivedPartNum = findPartNum(byteCode)
    receivedfileNameNum = findfileNameNum(byteCode)
    receivedLastFile = findLastFile(byteCode)

    # if a worker sends a delcaration of existence
    if receivedMessageCode == 7:
        # gets the index of the current workers address
        currentWorker = findIfUnitAlreadyDeclared(workerAddresses, address)
        byteCodeToSend = createByteCode(5, 0, 0, 0, 1)
        confirmation = "Declared worker {}".format(currentWorker)
        print(confirmation)
        bytesToSend = byteCodeToSend
        UDPIngressSocket.sendto(bytesToSend, workerAddresses[currentWorker])

    # if a client sends a request
    if receivedMessageCode == 0:
        # the client message gets recorded and sorted into the appropriate variables
        currentClient = findIfUnitAlreadyDeclared(clientAddresses, address)
        # if workers have declared themselves, the ingress will choose a random one and send on the clients request to them
        if len(workerAddresses) != 0:
            currentWorker = selectAvailableWorker()
            byteCodeToSend = createByteCode(4, currentClient, 0, receivedfileNameNum, 1)
            print("Received a request from client for a file")
            bytesToSend = byteCodeToSend
            UDPIngressSocket.sendto(bytesToSend, currentWorker)

    # if a worker sends confirmation
    if receivedMessageCode == 3:
        currentClient = findClient(byteCode)
        byteCodeToSend = createByteCode(5, currentClient, receivedPartNum, receivedfileNameNum, receivedLastFile)
        bytesToSend = message
        UDPIngressSocket.sendto(bytesToSend, clientAddresses[currentClient])
        # POSSIBLE BUG: COULD RECEIVE LAST FILE BEFORE ALL FILES ARE RECEIVED LOL
        if receivedLastFile == 1:
            makeWorkerAvailabe(address)
            print("Forwarded file to client")
