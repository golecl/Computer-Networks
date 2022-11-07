# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 1
from commonFunctions import *

localIP = "127.0.0.1"
localPort = 49668
clientAddresses = ['0']
workerAddresses = []
unavailableWorkers = []
currentClient = -1
currentWorker = -1
requestQueue = []
currentRequest = 0

# selects available worker from list of workers and moves them to unavailable list
def selectAvailableWorker():
    currentWorker = workerAddresses.pop(randrange(len(workerAddresses)))
    unavailableWorkers.append(currentWorker)
    return currentWorker

# appends the request queue
def updateRequestQueue(requests):
    for currRequest in requests:
        client = findIfUnitAlreadyDeclared(clientAddresses, currRequest[1])
        request = createHeader(0, client, 0, findfileNameNum(currRequest[0]), 1)
        requestQueue.append(request)


# create a datagram socket
UDPIngressSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# bind to address and ip
UDPIngressSocket.bind((localIP, localPort))

print("UDP ingress up and listening")

# listen for incoming datagrams
while True:
    # constantly trying to receive messages
    UDPIngressSocket.settimeout(timeout*2)

    if currentRequest != 0:
        # if workers have declared themselves, the ingress will choose a random one and send on the clients request to them
        if len(workerAddresses) != 0:
            currentWorker = selectAvailableWorker()
            currentClient = findClient(currentRequest)
            UDPIngressSocket.sendto(currentRequest, currentWorker)
    else: # currentRequest == 0:
        if len(requestQueue) > 0:
            currentRequest = requestQueue.pop()
    # tries to receive packets, if it times out it restarts the while loop
    try:
        bytesAddressPair = UDPIngressSocket.recvfrom(bufferSize)
    except:
        continue
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    header = getHeaderFromMessage(message)

    # extracts below variables from header for ease of use
    receivedMessageCode = findCode(header)
    receivedPartNum = findPartNum(header)
    receivedfileNameNum = findfileNameNum(header)

    # if a worker sends a delcaration of existence
    if receivedMessageCode == 1:
        # gets the index of the current workers address
        currentWorker = findIfUnitAlreadyDeclared(workerAddresses, address)
        print("Declared worker number {}".format(currentWorker))

    # if a client sends a request
    if receivedMessageCode == 0:
        # the client message gets recorded and sorted into the appropriate variables
        # create a request and either add it to queue or make it the current 
        request = [[createHeader(0, 0, 0, receivedfileNameNum, 1), address]]
        updateRequestQueue(request)

    # if a worker sends confirmation
    if receivedMessageCode == 2:
        currentClient = findClient(header)
        # receives packets from worker
        stopAndWaitResults = stopAndWaitARQReceiver(UDPIngressSocket)
        receivedPackets = stopAndWaitResults[0]
        receivedRequests = stopAndWaitResults[1]
        # if requests received during arq, adds them to queue
        if receivedRequests != 0:
            for request in receivedRequests:
                updateRequestQueue(request)
        # sends packets to client
        receivedRequests = stopAndWaitARQSender(UDPIngressSocket, clientAddresses[currentClient], receivedPackets)
        # if requests received during arq, adds them to queue
        if receivedRequests != 0:
            for request in receivedRequests:
                updateRequestQueue(request)
        currentRequest = 0

