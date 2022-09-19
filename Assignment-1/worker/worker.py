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

codeBytes = 1
clientBytes = 2
partNumBytes = 2
totPartsBytes = 2
totalHeaderBytes = codeBytes + clientBytes + partNumBytes + totPartsBytes

# creates the Byte code used to identify the action, client, current file part, and total file parts
def createByteCode(messageCode, client, partNumber, totalParts):
    msgCodeByte = messageCode.to_bytes(codeBytes, 'big') # creates a 8 bit Byte number of the message code
    clientByte = client.to_bytes(clientBytes, 'big') # creates a 16 bit Byte number of the client number
    partNum = partNumber.to_bytes(partNumBytes, 'big') # creates a byte sized number
    partTot = totalParts.to_bytes(totPartsBytes, 'big')
    ByteCode = msgCodeByte + clientByte + partNum + partTot
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
def findTotalPartNum(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes
    end = start + totPartsBytes
    return int.from_bytes(message[start:end], 'big')

def getStringCodeFromByteCode(byteCode):
    code = findCode(byteCode)
    client = findClient(byteCode)
    partNum = findPartNum(byteCode)
    totPartNum = findTotalPartNum(byteCode)
    string = f'{code:0{codeBytes*8}}' + f'{client:0{clientBytes*8}}' + f'{partNum:0{partNumBytes*8}}' + f'{totPartNum:0{totPartsBytes*8}}'
    return string

# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("127.0.0.1", 49668)
bufferSize = 1024

# create a UDP socket at Worker side
UDPWorkerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# sends declaration
byteCodeToSend = createByteCode(7, 0, 0, 0);
declarationFromWorker = "{} I have sent a declaration yassss!!!!! [Code: {}]".format(getStringCodeFromByteCode(byteCodeToSend), messageCodes[7])
bytesToSend = byteCodeToSend + str.encode(declarationFromWorker)
print(declarationFromWorker)
UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)

while True:
    # listens out for messages sent by ingress
    bytesReceivedFromIngress = UDPWorkerSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    byteCode = getByteCodeFromMessage(bytesMessageFromIngress)

    receivedMessageCode = findCode(byteCode)
    receivedPartNum = findPartNum(byteCode)
    receivedTotalPartNum = findTotalPartNum(byteCode)
    receivedClientNum = findClient(byteCode)


    # if the ingress is sending on a request made by a client
    if receivedMessageCode == 4:
        byteCodeToSend = createByteCode(3, receivedClientNum, receivedPartNum, receivedTotalPartNum)
        msgWhenReceived = "{} imagine not receiving request from client! couldnt be me [Code: {}]".format(getStringCodeFromByteCode(byteCodeToSend), messageCodes[3])
        print(msgWhenReceived)
        bytesToSend = byteCodeToSend + str.encode(msgWhenReceived)
        UDPWorkerSocket.sendto(bytesToSend, IngressAddressPort)
