# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 1
from commonFunctions import *

# input the file index to be partitioned and the client it is meant to be sent to
# returns an array of the bytes that need to be sent with the header included
def packetPartitioning(fileIndex, clientNumber):
    partitionedFileBytes = []
    file = open(availableFiles[fileIndex], "rb")
    fileBytes = file.read() # reads in the file and saves as an array of bytes
    numberOfParts = math.ceil(len(fileBytes)/maxDataSize) # determines how many partitions there will be
    for x in range(numberOfParts):
        if x < numberOfParts - 1:
            partition = fileBytes[x*maxDataSize : (x+1)*maxDataSize]
            lastFile = 0
        else:
            partition = fileBytes[x*maxDataSize : len(fileBytes)]
            lastFile = 1
        header = createHeader(2, clientNumber, x, fileIndex, lastFile)
        partition = header + partition
        partitionedFileBytes.append(partition)
    return partitionedFileBytes

IngressAddressPort = ("127.0.0.1", 49668)

# create a UDP socket at Worker side
UDPWorkerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# sends declaration to ingress
headerToSend = createHeader(1, 0, 0, 0, 1)
bytesToSend = headerToSend
UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)

while True:
    # listens out for messages sent by ingress
    bytesReceivedFromIngress = UDPWorkerSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    
    header = getHeaderFromMessage(bytesMessageFromIngress)

    receivedMessageCode = findCode(header)
    receivedfileNameNum = findfileNameNum(header)
    receivedClientNum = findClient(header)

    # if the ingress is sending on a request made by a client
    # it sends back all files requested in 1 or more partitions
    if receivedMessageCode == 0:
        filePartitions = packetPartitioning(receivedfileNameNum, receivedClientNum)
        stopAndWaitARQSender(UDPWorkerSocket, IngressAddressPort, filePartitions)
        print("\nWorker sent file '{}'".format(availableFiles[receivedfileNameNum]))
