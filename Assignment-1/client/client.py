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

# no assigned client number yet
assignedClientNumber = 0
# declaration message so that ingress knows who its clients are, it is not necessary but was nice for debugging
# might delete later
declared = False
# empty IP number as it will find its own ip which is assigned by docker
IngressAddressPort = ("", 49668)
bufferSize = 1024

# create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

numberOfRequests = 0
# send initial request to Ingress using created UDP socket
# POSSIBLE BUG: has to be done at least once before the while loop? i assume it is because it keeps listening for a message from Ingress
# says the request number and then a human readable code, then the Byte code
byteCodeToSend = createByteCode(0, assignedClientNumber, 0, 0)
requestFromClient = "{} We have done this {} times! Please tell worker I said hi [Code: {}]".format(getStringCodeFromByteCode(byteCodeToSend), numberOfRequests, messageCodes[0])
print(requestFromClient)
bytesToSend = byteCodeToSend + str.encode(requestFromClient)
UDPClientSocket.sendto(bytesToSend, IngressAddressPort)
numberOfRequests+=1

# seeks out reply from ingress
while True:
    bytesReceivedFromIngress = UDPClientSocket.recvfrom(bufferSize)
    bytesMessageFromIngress = bytesReceivedFromIngress[0]
    byteCode = getByteCodeFromMessage(bytesMessageFromIngress)

    receivedMessageCode = findCode(byteCode)
    receivedPartNum = findPartNum(byteCode)
    receivedTotalPartNum = findTotalPartNum(byteCode)

    # if confirmation from ingress is received
    if receivedMessageCode == 5:
        byteCodeToSend = createByteCode(5, assignedClientNumber, receivedPartNum, receivedTotalPartNum)
        msgWhenReceived = "{} Oh mein got!!!! I received zat message so gut!!!!!!!! [Code: {}]".format(getStringCodeFromByteCode(byteCodeToSend), messageCodes[1])
        print(msgWhenReceived)

    # send request to Ingress using created UDP socket 3 times
    if numberOfRequests < 3:
        byteCodeToSend = createByteCode(0, assignedClientNumber, 0, 0)
        requestFromClient = "{} We have done this {} times! Please tell worker I said hi [Code: {}]".format(getStringCodeFromByteCode(byteCodeToSend), numberOfRequests, messageCodes[0])
        print(requestFromClient)
        bytesToSend = byteCodeToSend + str.encode(requestFromClient)
        UDPClientSocket.sendto(bytesToSend, IngressAddressPort)
        numberOfRequests+=1
