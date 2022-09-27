import socket
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

availableFiles = ["test1.txt", "test2.txt", "test3.txt", "test4.txt", "bo_minion.png", "block.png"]

# TODO: IMPLEMENT SORTING ALGORITHM FOR THE FILE PARTITIONS

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

def removeByteCode(message):
    finalFile = message[totalHeaderBytes - 1: len(message)]
    return finalFile

def bubbleSort(partitionArray):
    n = len(partitionArray)
    for i in range(n):
        for j in range(0, n-i-1):
            if findPartNum(partitionArray[j]) > findPartNum(partitionArray[j+1]):
                partitionArray[j], partitionArray[j+1] = partitionArray[j+1], partitionArray[j]

def rebuildFile(partitionArray):
    bubbleSort(partitionArray)
    finalFile = b''
    fileNumber = findfileNameNum(partitionArray[0])
    for x in partitionArray:
        finalFile = finalFile + removeByteCode(x)
    finalFile = finalFile[1:len(finalFile)]
    fileInfo = [fileNumber, finalFile]
    return fileInfo

# no assigned client number yet
assignedClientNumber = 0
# declaration message so that ingress knows who its clients are, it is not necessary but was nice for debugging
# might delete later
declared = False
# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("", 49668)
bufferSize = 65500

# create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# send initial request to Ingress using created UDP socket
# POSSIBLE BUG: has to be done at least once before the while loop? i assume it is because it keeps listening for a message from Ingress
# says the request number and then a human readable code, then the Byte code
#fileChoice = randrange(len(availableFiles))
fileChoice = 5
#print("This is a random file choice: ", fileChoice + 1)
byteCodeToSend = createByteCode(0, assignedClientNumber, 0, fileChoice, 1)
print("\nRequesting file '{}'".format(availableFiles[fileChoice]))
bytesToSend = byteCodeToSend
UDPClientSocket.sendto(bytesToSend, IngressAddressPort)

receivedFiles = []

# seeks out reply from ingress
totalFileParts = -1
while True:

    bytesReceivedFromIngress = UDPClientSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    byteCode = getByteCodeFromMessage(bytesMessageFromIngress)

    receivedMessageCode = findCode(byteCode)
    receivedPartNum = findPartNum(byteCode)
    receivedfileNameNum = findfileNameNum(byteCode)
    receivedLastFile = findLastFile(byteCode)

    # if confirmation from ingress is received
    if receivedMessageCode == 3:
        receivedFiles.insert(receivedPartNum, bytesMessageFromIngress)
        print("This many packets have been received: {}".format(len(receivedFiles)))
        if receivedLastFile == 1:
            totalFileParts = receivedPartNum
        if len(receivedFiles) - 1 == totalFileParts:
            print("gotted 4")
            print("This many packets have been received: {}".format(len(receivedFiles)))
            if len(receivedFiles) - 1 == totalFileParts:
                print("got here 0")
                finalFileInfo = rebuildFile(receivedFiles)
                print("got here 1")
                file = open(r"../endFiles/{}".format(availableFiles[receivedfileNameNum]), "w")
                file = open(r"../endFiles/{}".format(availableFiles[receivedfileNameNum]), "wb")
                print("got here 2")
                finalFileData = finalFileInfo[1]
                #print(finalFileData)
                file.write(finalFileData)
                file.close()
                print("Received the file: '{}'".format(availableFiles[finalFileInfo[0]]))
                receivedFiles = []
