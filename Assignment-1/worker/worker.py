from commonFunctions import *
from listOfFiles import availableFiles

# message codes:
# 0 = client request for file
# 1 = worker declaration
# 2 = worker file sent
# 3 = ACK
# 4 = NACK

maxDataSize = bufferSize - totalHeaderBytes - 10

# input the file index to be partitioned and the client it is meant to be sent to
# returns an array of the bytes that need to be sent with the byte code included
def packetPartitioning(fileIndex, clientNumber):
    partitionedFileBytes = []
    file = open(availableFiles[fileIndex], "rb")
    fileBytes = file.read() # reads in the file and saves as an array of bytes
    numberOfParts = math.ceil(len(fileBytes)/maxDataSize) # determines how many partitions there will be
    windowSize = createWindowSize(fileIndex)
    for x in range(numberOfParts):
        if x < numberOfParts - 1:
            partition = fileBytes[x*maxDataSize : (x+1)*maxDataSize]
            lastFileConfirmation = 0
        else:
            partition = fileBytes[x*maxDataSize : len(fileBytes)]
            lastFileConfirmation = 1
        windowLastInt = createWindowLastInt(windowSize, lastFileConfirmation)
        byteCode = createByteCode(2, clientNumber, x, fileIndex, windowLastInt)
        partition = byteCode + partition
        partitionedFileBytes.append(partition)
    return partitionedFileBytes

IngressAddressPort = ("127.0.0.1", 49668)
# create a UDP socket at Worker side
UDPWorkerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# sends declaration to ingress
byteCodeToSend = createByteCode(1, 0, 0, 0, 1)
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
    if receivedMessageCode == 0:
        print("processing request")
        print("This is my original socket ", UDPWorkerSocket)
        filePartitions = packetPartitioning(receivedfileNameNum, receivedClientNum)
        print("got here 1")
        selectiveARQSender(UDPWorkerSocket, IngressAddressPort, filePartitions)
        print("got here 2")

        #print("This many packets have been sent: {}".format(windowSize * windowCounter)
        #print("Have sent the entire file '{}'".format(availableFiles[findfileNameNum(bytesToSend)]))
