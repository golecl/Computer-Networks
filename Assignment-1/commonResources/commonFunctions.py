# imports all needed imports for all other files
from random import randrange
import socket
import math
from listOfFiles import *

# each datagram will contain 8 bytes in the beggining describing all of the useful information
# this is called the header
# this information is operation/message code, client number, part number, file name index, last file boolean

# message codes:
# 0 = client request for file
# 1 = worker declaration
# 2 = worker file sent
# 3 = ACK
# 4 = NACK

bufferSize = 65500

# function used to find an item on a list or add it if it does not exist on the list yet
def findIfUnitAlreadyDeclared(list, item):
    # if the item is already in the list, it returns its index
    try:
        index = list.index(item)
        return index
    # if it is not already on the list it adds it to the end and returns its index
    except:
        list.append(item)
        return list.index(item)

# ~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HEADER SECTION ~~~~~~~~~~~~~~~~~~~~~

# this sets the number of bytes that each section of the header takes up
codeBytes = 1
clientBytes = 2
partNumBytes = 2
fileNameBytes = 2
lastByte = 1

totalHeaderBytes = codeBytes + clientBytes + partNumBytes + fileNameBytes + lastByte
maxDataSize = bufferSize - totalHeaderBytes - 10
# sets the timeout for all transmission
timeout = 3

# creates the header used to identify the action, client, current file part, and total file parts
def createHeader(messageCode, client, partNumber, fileNames, lastFile):
    msgCodeByte = messageCode.to_bytes(codeBytes, 'big') # creates a Byte number of the message code
    clientByte = client.to_bytes(clientBytes, 'big') # creates 2 bytes number of the client number
    partNum = partNumber.to_bytes(partNumBytes, 'big') # creates a byte sized number of the part number
    fileNameNum = fileNames.to_bytes(fileNameBytes, 'big') # creates 2 byte sized number of the file name index
    lastFile = lastFile.to_bytes(lastByte, 'big') # creates byte to represent whether the file is the last or not
    Header = msgCodeByte + clientByte + partNum + fileNameNum + lastFile
    return Header

# gets the header from a packet
# NEEDS TO BE PASSED IN ENCODED AS BYTES OTHERWISE WILL NOT WORK
def getHeaderFromMessage(message):
    Header = message[0:totalHeaderBytes]
    return Header

# FOR ALL "find" FUNCTIONS BELOW:
    # ONLY PASS IN THE FIRST FEW BYTES OF A MESSAGE BECAUSE OTHERWISE IT MIGHT BE SLOW

# gets the message code from a Byte string in form of int
def findCode(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getHeaderFromMessage(message)
    #if the header only has been passed in
    start = 0
    end = start + codeBytes
    return int.from_bytes(message[start:end], 'big')


# gets the client number from a Byte string in form of int
def findClient(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getHeaderFromMessage(message)
    #if the header only has been passed in
    start = codeBytes
    end = start + clientBytes
    return int.from_bytes(message[start:end], 'big')

# gets the part number from a Byte string in form of int
def findPartNum(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getHeaderFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes
    end = start + partNumBytes
    return int.from_bytes(message[start:end], 'big')

# gets the file name number of parts from a Byte string in form of int
def findfileNameNum(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getHeaderFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes
    end = start + fileNameBytes
    return int.from_bytes(message[start:end], 'big')

# gets last file confirmation byte in form of int
def findLastFile(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getHeaderFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes + fileNameBytes
    end = start + lastByte
    # returns whether the packet is the last in the file
    return int.from_bytes(message[start:end], 'big')

def removeHeader(message):
    finalFile = message[totalHeaderBytes:]
    return finalFile

# ~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~ sender ARQ subsection ~~~~~~~~~~~~~~~~~~~~

# listens for ACKs and NACKs and returns the received packet/ received requests
def listenForACK(socketName):
    socketName.settimeout(timeout)
    receivedRequests = []
    resultPair = [0]*2
    while True:
        # listen for packets, if timed out return 0
        try:
            bytesReceived = socketName.recvfrom(bufferSize)
            operation = findCode(bytesReceived[0])
        except:
            resultPair[0] = 0
            return resultPair
        # if new request received, add to list
        if operation == 0:
            receivedRequests.append(bytesReceived)
            resultPair[1] = receivedRequests
        # if ACK received return 1
        if operation == 3:
            resultPair[0] = 1
            return resultPair
        # if NACK received, return 0
        if operation == 4:
            resultPair[0] = 0
            return resultPair

# takes in sender socket, the address port of the reciever and the packets to send
def stopAndWaitARQSender(senderSocket, addressPort, allPacketPartitions):
    counter = 0
    receivedRequests = []
    while True:
        nextPacket = 0
        if counter < len(allPacketPartitions):
            # set the current packet to the correct packet
            currentPacket = allPacketPartitions[counter]
        else:
            # if not possible, reached the end and break function
            senderSocket.settimeout(None)
            break
        while nextPacket == 0:
            # if ACK not received, send the packet
            senderSocket.sendto(currentPacket, addressPort)
            listenPair = listenForACK(senderSocket)
            nextPacket = listenPair[0]
            if listenPair[1] != 0:
                # if request received, append list of requests
                receivedRequests.append(listenPair[1])
        if nextPacket == 1:
            # if ACK received, update the packet being sent
            counter += 1
    # return the requests received during the ARQ
    return receivedRequests

# ~~~~~~~~~~~~~~~ receiver ARQ subsection ~~~~~~~~~~~~~~~~~~~~

# listens for any received packets, returns the packets and requests
# also sends ACK for any received packet
def receiveFiles(receiverSocket, counter):
    receiverSocket.settimeout(timeout*2)
    returnPair = [0]*3
    receivedRequests = []
    while True:
        # try to receive packets
        try:
            receivedPair = receiverSocket.recvfrom(bufferSize)
            packet = receivedPair[0]
            address = receivedPair[1]
            packetNumber = findPartNum(packet)
            operation = findCode(packet)
            # if socket receives new request while listening for packets
            if operation == 0:
                receivedRequests.append(receivedPair)
                returnPair[2] = receivedRequests
            elif operation == 2:
                if packetNumber == counter:
                    # create ACK and send it 
                    bytesToSend = createHeader(3, findClient(packet), findPartNum(packet), 0, 0)
                    receiverSocket.sendto(bytesToSend, address)
                    returnPair[1] = packet
                    if findLastFile(packet) == 0:
                        returnPair[0] = 1
                        return returnPair
                    else:
                        returnPair[0] = -1
                        return returnPair
        # if packet not received, do not move the window
        except Exception:
            returnPair[0] = 0
            returnPair[1] = 0
            return returnPair

# takes in receiver socket along with the first packet, returns received packets and requests
def stopAndWaitARQReceiver(receiverSocket, firstPacket):
    counter = 0
    totalReceivedPackets = []
    packetsAndRequests = [[0]]*2
    receivedRequests = []
    address = firstPacket[1]
    clientNumber = findClient(firstPacket[0])
    fileNameNum = findfileNameNum(firstPacket[0])
    mostRecentPacket = 0
    received = 0
    while True:
        receivedPair = receiveFiles(receiverSocket, counter)
        mostRecentPacket = receivedPair[1]
        received = receivedPair[0]
        # if requests were received during the stop and wait arq
        if receivedPair[2] != 0:
            receivedRequests.append(receivedPair[2])
        # if the packet received is the last packet, save it and break the loop
        if received == -1:
            totalReceivedPackets.append(mostRecentPacket)
            break
        # if not received, send NACK
        if received == 0:
            bytesToSend = createHeader(4, clientNumber, counter, fileNameNum, 0)
            receiverSocket.sendto(bytesToSend, address)
        # if received, add to list and move on to next packet
        if received == 1:
            counter += 1
            totalReceivedPackets.append(mostRecentPacket)
    receiverSocket.settimeout(None)
    packetsAndRequests[0] = totalReceivedPackets 
    packetsAndRequests[1] = receivedRequests
    return packetsAndRequests