import socket
import time
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

assignedWorkerNumber = -1
declarationFromWorker = "Hello UDP Ingress this is Worker! [Code: {}] {}".format(messageCodes[7], createBinaryCode(7, -1, -1))
declared = 0
# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("127.0.0.1", 49668)
bufferSize = 1024


# create a UDP socket at Worker side
UDPWorkerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

bytesToSend = str.encode(declarationFromWorker)
UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)

# send to Ingress using created UDP socket
if declared == 0:
    bytesReceivedFromIngress = UDPWorkerSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    stringMessage = bytesMessageFromIngress.decode()
    assignedWorkerNumber = findWorker(getBinaryCodeFromMessage(stringMessage))
    print("I have sent a declaration yassss!!!!! [Code: {}] {}".format(messageCodes[7], createBinaryCode(7, -1, assignedWorkerNumber)))
    declared = 1
    # if declaration complete, no longer send message to ingress and can take orders from ingress

while True:
    # listens out for messages sent by ingress
    bytesReceivedFromIngress = UDPWorkerSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    stringMessage = bytesMessageFromIngress.decode()
    binaryCode = getBinaryCodeFromMessage(stringMessage)
    receivedMessageCode = findCode(binaryCode)

    # if the ingress is sending on a request made by a client
    if receivedMessageCode == 4:
        msgWhenReceived = "imagine not receiving request from client! couldnt be me [Code: {}] {}".format(messageCodes[3], createBinaryCode(3, findClient(binaryCode), assignedWorkerNumber))
        print(msgWhenReceived)
        bytesToSend = str.encode(msgWhenReceived)
        UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)
