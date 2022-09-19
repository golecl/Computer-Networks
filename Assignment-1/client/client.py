import socket
messageCodes = ["r3qu35t-cl13nt","c0nf1rmat10n-cl13nt", "r3qu35t-w0rk3r",
                "c0nf1rmat10n-w0rk3r", "r3qu35t-1ngr355", "c0nf1rmat10n-1ngre55",
                 "d3clarat10n-cl13nt", "d3clarat10n-w0rk3r"]
# code r3qu35t = request
# code c0nf1rmat10n = confirmation
# code d3clarat10n" declaration
# code "cl13nt" = client
# code "w0rk3r" = worker
# code "1ngr355" = ingress

clientWorkerBits = 16
codeBits = 4

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
def getBinaryCodeFromMessage(message):
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

# no assigned client number yet
assignedClientNumber = -1
# declaration message so that ingress knows who its clients are, it is not necessary but was nice for debugging
# might delete later
declarationFromClient = "Hello UDP Ingress this is Client! [Code: {}] {}".format(messageCodes[6], createBinaryCode(6, -1, -1))
declared = False
# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("", 49668)
bufferSize = 1024

# create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# encodes message into bytes instead of a regular string
bytesToSend = str.encode(declarationFromClient)
UDPClientSocket.sendto(bytesToSend, IngressAddressPort)

# send to Ingress using created UDP socket
if declared == False:
    bytesReceivedFromIngress = UDPClientSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    stringMessage = bytesMessageFromIngress.decode()
    assignedClientNumber = findClient(getBinaryCodeFromMessage(stringMessage))
    print("just declared ;) [Code: {}] {}".format(messageCodes[6], createBinaryCode(6, assignedClientNumber, -1)))
    declared = True
    # if declaration complete, can now send requests to ingress

numberOfRequests = 0
# send initial request to Ingress using created UDP socket
# POSSIBLE BUG: has to be done at least once before the while loop? i assume it is because it keeps listening for a message from Ingress
# says the request number and then a human readable code, then the binary code
requestFromClient = "We have done this {} times! Please tell worker I said hi [Code: {}] {}".format(numberOfRequests, messageCodes[0], createBinaryCode(0, assignedClientNumber, -1))
print(requestFromClient)
bytesToSend = str.encode(requestFromClient)
UDPClientSocket.sendto(bytesToSend, IngressAddressPort)
numberOfRequests+=1

# seeks out reply from ingress
while True:
    bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
    msgFromIngress = bytesAddressPair[0]
    # message is received in bytes so it has to be decoded
    stringMessage = msgFromIngress.decode()
    # finds the action code in the binary code
    receivedMessageCode = findCode(getBinaryCodeFromMessage(stringMessage))

    # if confirmation from ingress is received
    if receivedMessageCode == 5:
        # it will find which worker completed its request which isnt exactly necessary but it is useful for debugging
        worker = findWorker(getBinaryCodeFromMessage(stringMessage))
        msgWhenReceived = "Oh mein got!!!! I received zat message so gut!!!!!!!! [Code: {}] {}".format(messageCodes[1], createBinaryCode(1, assignedClientNumber, worker))
        print(msgWhenReceived)

    # send request to Ingress using created UDP socket 3 times
    if numberOfRequests < 3:
        requestFromClient = "We have done this {} times! Please tell worker I said hi [Code: {}] {}".format(numberOfRequests, messageCodes[0], createBinaryCode(0, assignedClientNumber, -1))
        print(requestFromClient)
        bytesToSend = str.encode(requestFromClient)
        UDPClientSocket.sendto(bytesToSend, IngressAddressPort)
        numberOfRequests+=1
