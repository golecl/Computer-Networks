from commonFunctions import *

# message codes:
# 0 = client request for file
# 1 = worker declaration
# 2 = worker file sent

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
clientAddresses = ['0']
workerAddresses = []
unavailableWorkers = []
currentClient = -1
currentWorker = -1

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
counter = 0
while True:
    # constantly trying to receive messages
    counter += 1
    bytesAddressPair = UDPIngressSocket.recvfrom(bufferSize)
    print("Counter: {}".format(counter))
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    byteCode = getByteCodeFromMessage(message)

    receivedMessageCode = findCode(byteCode)
    receivedPartNum = findPartNum(byteCode)
    receivedfileNameNum = findfileNameNum(byteCode)
    receivedLastFile = findLastFile(byteCode)

    # if a worker sends a delcaration of existence
    if receivedMessageCode == 1:
        # gets the index of the current workers address
        currentWorker = findIfUnitAlreadyDeclared(workerAddresses, address)
        print(address)

    # if a client sends a request
    if receivedMessageCode == 0:
        # the client message gets recorded and sorted into the appropriate variables
        currentClient = findIfUnitAlreadyDeclared(clientAddresses, address)
        # if workers have declared themselves, the ingress will choose a random one and send on the clients request to them
        if len(workerAddresses) != 0:
            currentWorker = selectAvailableWorker()
            byteCodeToSend = createByteCode(0, currentClient, 0, receivedfileNameNum, 1)
            print("Received a request from client for a file")
            bytesToSend = byteCodeToSend
            print("ingress sends request to ", currentWorker)
            UDPIngressSocket.sendto(bytesToSend, currentWorker)

    # if a worker sends confirmation
    if receivedMessageCode == 2:
        currentClient = findClient(byteCode)
        receivedPackets = selectiveARQReceiver(UDPIngressSocket, address, message)
        selectiveARQSender(UDPIngressSocket, clientAddresses[currentClient], receivedPackets)
