from commonFunctions import *

# takes in received partitions and reassembles it
def rebuildFile(partitionArray):
    partitionArray.sort(key = findPartNum)
    fileNumber = findfileNameNum(partitionArray[0])
    for index in range(len(partitionArray)):
        partitionArray[index] = removeHeader(partitionArray[index])
    finalFile = b''.join(partitionArray)
    fileInfo = [fileNumber, finalFile]
    return fileInfo

# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("", 49668)

# create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# send request to Ingress using created UDP socket
fileChoice = randrange(len(availableFiles)) # sends request for random file
# fileChoice = len(availableFiles) - 1      # sends request for last file, used mostly for debugging
headerToSend = createHeader(0, 0, 0, fileChoice, 1)
print("Requesting file '{}'".format(availableFiles[fileChoice]))
UDPClientSocket.sendto(headerToSend, IngressAddressPort)

receivedFiles = []
# seeks out reply from ingress
while True:
    bytesReceivedFromIngress = UDPClientSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    address = bytesReceivedFromIngress[1]
    header = getHeaderFromMessage(bytesMessageFromIngress)

    # save sections of header as variables for ease of use
    receivedMessageCode = findCode(header)
    receivedPartNum = findPartNum(header)
    receivedfileNameNum = findfileNameNum(header)

    # if confirmation from ingress is received
    if receivedMessageCode == 2:
        receivedFiles = stopAndWaitARQReceiver(UDPClientSocket, bytesReceivedFromIngress)[0]
        finalFileInfo = rebuildFile(receivedFiles)
        file = open(r"../endFiles/{}".format(availableFiles[receivedfileNameNum]), "wb")
        finalFileData = finalFileInfo[1]
        file.write(finalFileData)
        file.close()
        print("Client received the file: '{}'".format(availableFiles[finalFileInfo[0]]))
        receivedFiles = []
