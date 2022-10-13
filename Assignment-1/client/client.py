from commonFunctions import *

# message codes:
# 0 = client request for file
# 1 = worker declaration
# 2 = worker file sent

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
    #finalFile = finalFile[1:]
    fileInfo = [fileNumber, finalFile]
    return fileInfo

# declaration message so that ingress knows who its clients are, it is not necessary but was nice for debugging
# might delete later
declared = False
# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("", 49668)

# create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# send initial request to Ingress using created UDP socket
# POSSIBLE BUG: has to be done at least once before the while loop? i assume it is because it keeps listening for a message from Ingress
# says the request number and then a human readable code, then the Byte code
#fileChoice = randrange(len(availableFiles))
fileChoice = 4
#print("This is a random file choice: ", fileChoice + 1)
byteCodeToSend = createByteCode(0, 0, 0, fileChoice, 1)
print("\nRequesting file '{}'".format(availableFiles[fileChoice]))
bytesToSend = byteCodeToSend
UDPClientSocket.sendto(bytesToSend, IngressAddressPort)

receivedFiles = []

# seeks out reply from ingress
totalFileParts = -1
while True:

    bytesReceivedFromIngress = UDPClientSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    address = bytesReceivedFromIngress[1]
    byteCode = getByteCodeFromMessage(bytesMessageFromIngress)

    receivedMessageCode = findCode(byteCode)
    receivedPartNum = findPartNum(byteCode)
    receivedfileNameNum = findfileNameNum(byteCode)
    receivedLastFile = findLastFile(byteCode)

    # if confirmation from ingress is received
    if receivedMessageCode == 2:
        receivedFiles = selectiveARQReceiver(UDPClientSocket, address, bytesMessageFromIngress)
        finalFileInfo = rebuildFile(receivedFiles)
        file = open(r"../endFiles/{}".format(availableFiles[receivedfileNameNum]), "wb")
        finalFileData = finalFileInfo[1]
        file.write(finalFileData)
        file.close()
        print("Received the file: '{}'".format(availableFiles[finalFileInfo[0]]))
        receivedFiles = []
