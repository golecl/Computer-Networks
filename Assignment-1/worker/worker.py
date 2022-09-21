import socket
import math
messageCodes = ["r3qu35t-cl13nt","c0nf1rmat10n-cl13nt", "r3qu35t-w0rk3r",
                "c0nf1rmat10n-w0rk3r", "r3qu35t-1ngr355", "c0nf1rmat10n-1ngre55",
                 "d3clarat10n-cl13nt", "d3clarat10n-w0rk3r"]
# code r3qu35t = request
# code c0nf1rmat10n = confirmation
# code d3clarat10n" declaration
# code "cl13nt" = client
# code "w0rk3r" = worker
# code "1ngr355" = ingress

availableFiles = ["test1.txt", "test2.txt", "test3.txt", "test4.txt"]

codeBytes = 1
clientBytes = 2
partNumBytes = 2
fileNameBytes = 2
lastFileBytes = 1
totalHeaderBytes = codeBytes + clientBytes + partNumBytes + fileNameBytes + lastFileBytes
bufferSize = 20000
maxDataSize = bufferSize - totalHeaderBytes - 10

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

# input the file index to be partitioned and the client it is meant to be sent to
# returns an array of the bytes that need to be sent with the byte code included
def packetPartitioning(fileIndex, clientNumber):
    partitionedFileBytes = []
    file = open(availableFiles[fileIndex], "rb")
    fileBytes = file.read() # reads in the file and saves as an array of bytes
    numberOfParts = math.ceil(len(fileBytes)/maxDataSize) # determines how many partitions there will be
    for x in range(numberOfParts):
        if x < numberOfParts - 1:
            partition = fileBytes[x*maxDataSize : (x+1)*maxDataSize]
            lastFileConfirmation = 0
        else:
            partition = fileBytes[x*maxDataSize : len(fileBytes)]
            lastFileConfirmation = 1
        byteCode = createByteCode(3, clientNumber, x, fileIndex, lastFileConfirmation)
        partition = byteCode + partition
        partitionedFileBytes.append(partition)
    return partitionedFileBytes


# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("127.0.0.1", 49668)

# create a UDP socket at Worker side
UDPWorkerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# sends declaration
byteCodeToSend = createByteCode(7, 0, 0, 0, 1);
bytesToSend = byteCodeToSend
print("\nSent declaration to ingress")
UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)

while True:
    # listens out for messages sent by ingress
    bytesReceivedFromIngress = UDPWorkerSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    byteCode = getByteCodeFromMessage(bytesMessageFromIngress)

    receivedMessageCode = findCode(byteCode)
    receivedfileNameNum = findfileNameNum(byteCode)
    receivedClientNum = findClient(byteCode)

    # if the ingress is sending on a request made by a client
    # it sends back all files requested in 1 or more partitions
    if receivedMessageCode == 4:
        filePartitions = packetPartitioning(receivedfileNameNum, receivedClientNum)
        for x in filePartitions:
            bytesToSend = x
            if findLastFile(bytesToSend) == 1:
                print("Have sent the entire file '{}'".format(availableFiles[findfileNameNum(bytesToSend)]))
            UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)
