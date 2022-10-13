import multiprocessing
from random import randrange
from shutil import move
import socket
import random
import math
from listOfFiles import *

# message codes:
# 0 = client request for file
# 1 = worker declaration
# 2 = worker file sent
# 3 = ACK
# 4 = NACK

bufferSize = 65500

# function used to find worker addresses or add them if they do not exist on the list yet
def findIfUnitAlreadyDeclared(list, item):
    # if the unit is already in the list, it returns its index
    try:
        index = list.index(item)
        return index
    # if it is not already on the list it adds it to the end and returns its index
    except:
        list.append(item)
        return list.index(item)

# ~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~

codeBytes = 1
clientBytes = 2
partNumBytes = 2
fileNameBytes = 2
windowLastByte = 1
totalHeaderBytes = codeBytes + clientBytes + partNumBytes + fileNameBytes + windowLastByte
maxDataSize = bufferSize - totalHeaderBytes - 10

# creates the Byte code used to identify the action, client, current file part, and total file parts
def createByteCode(messageCode, client, partNumber, fileNames, windowLastFile):
    msgCodeByte = messageCode.to_bytes(codeBytes, 'big') # creates a 8 bit Byte number of the message code
    clientByte = client.to_bytes(clientBytes, 'big') # creates a 16 bit Byte number of the client number
    partNum = partNumber.to_bytes(partNumBytes, 'big') # creates a byte sized number
    fileNameNum = fileNames.to_bytes(fileNameBytes, 'big')
    windowLastFile = windowLastFile.to_bytes(windowLastByte, 'big')
    ByteCode = msgCodeByte + clientByte + partNum + fileNameNum + windowLastFile
    return ByteCode

# gets the Byte code from a string message
# NEEDS TO BE PASSED IN ENCODED AS BYTES OTHERWISE WILL NOT WORK
def getByteCodeFromMessage(message):
    ByteCode = message[0:totalHeaderBytes]
    return ByteCode

# FOR ALL "find" FUNCTIONS BELOW:
    # ONLY PASS IN THE FIRST FEW BYTES OF A MESSAGE BECAUSE OTHERWISE IT MIGHT BE SLOW

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

# gets the file name number of parts from a Byte string in form of int
def findfileNameNum(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes
    end = start + fileNameBytes
    return int.from_bytes(message[start:end], 'big')

# gets last file confirmation byte
def findLastFile(message):
    # if the header has not been detached from the rest of the data (slow)
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes + fileNameBytes
    end = start + windowLastByte
    # returns whether the byte is even or odd which determines whether or not it is the last file
    return int.from_bytes(message[start:end], 'big') % 2

def findWindowSize(message):
    if len(message) > totalHeaderBytes:
        message = getByteCodeFromMessage(message)
    #if the header only has been passed in
    start = codeBytes + clientBytes + partNumBytes + fileNameBytes
    end = start + windowLastByte
    # returns the first 7 bits of the byte as an int which is the window size
    return math.floor(int.from_bytes(message[start:end], 'big')/2)

def getStringCodeFromByteCode(byteCode):
    code = findCode(byteCode)
    client = findClient(byteCode)
    partNum = findPartNum(byteCode)
    fileNameNum = findfileNameNum(byteCode)
    lastFile = findLastFile(byteCode)
    string = f'{code:0{codeBytes*8}}' + f'{client:0{clientBytes*8}}' + f'{partNum:0{partNumBytes*8}}' + f'{fileNameNum:0{fileNameBytes*8}}' + f'{lastFile:0{windowLastByte*8}}'
    return string

def removeByteCode(message):
    finalFile = message[totalHeaderBytes - 1:]
    return finalFile

# ~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ERROR HANDLING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~

# input = int: the file index
# output = int: windowSize
def createWindowSize(fileIndex):
    file = open(availableFiles[fileIndex], "rb")
    fileBytes = file.read() # reads in the file and saves as an array of bytes
    numberOfParts = math.ceil(len(fileBytes)/maxDataSize) # determines how many partitions there will be
    maximumWindowSize = pow(2, windowLastByte*8 - 1) - 1
    # finds the largest factor under half the size and if it exceeds 127 (the number of bits allocates to window size)
    # it returns the largest factor under 127
    windowSize = min(findLargestFactor(numberOfParts, math.floor(numberOfParts/2)), findLargestFactor(numberOfParts, maximumWindowSize))
    return windowSize

# input = int: window size, int (bool really) = whether or not it is the last packet
# output = int: concatenation of windowSize + lastPacketBool
def createWindowLastInt(windowSize, lastFile):
    # this will turn it into an int that the first 7 bits of will represent the window size
    # and the last bit will represent whether or not it is the last file
    windowLastInt = windowSize*2 + lastFile
    return windowLastInt

# input = number to find largest factor of, limit of the largest factor
# output = largest factor in number under that limit
def findLargestFactor(number, threshold):
    largestFactor = 1
    for x in range(1, threshold):
        if number % x == 0:
            largestFactor = x
    return largestFactor

def listenForACK(socketName, packetsInWindow, timeout, indexOffset):
    socketName.settimeout(timeout)
    packetsLeft = 0
    for packet in packetsInWindow:
        if packet != 0:
            packetsLeft += 1
    while True:
        try:
            bytesReceived = socketName.recvfrom(bufferSize)
        except:
            return packetsInWindow
        bytesMessage = bytesReceived[0]
        byteCode = getByteCodeFromMessage(bytesMessage)
        operation = findCode(byteCode)
        if operation == 3:
            partNum = findPartNum(byteCode)
            packetsInWindow[partNum - indexOffset] = 0
            packetsLeft -= 1
            if packetsLeft == 0:
                return 1
        elif operation == 4:
            partNum = findPartNum(byteCode)
            packetsInWindow[partNum - indexOffset] = bytesMessage
            for packet in packetsInWindow:
                if packet != 0:
                    packetsLeft += 1
        if packetsLeft == 0:
            return 1

# takes in sender socket, the address port of the reciever and the packets to send
def selectiveARQSender(senderSocket, addressPort, allPacketPartitions):
    windowSize = findWindowSize(allPacketPartitions[0])
    windowCounter = 0
    timeout = windowSize*4
    while True:
        indexOffset = windowCounter*windowSize
        if (windowCounter*windowSize) < len(allPacketPartitions):
            # set the packets in the window to the packets in the correct range from total packets
            packetsInWindow = allPacketPartitions[windowCounter*windowSize : (windowCounter + 1)*windowSize]
        else:
            # if not possible, reached the end and break function
            print("SENT ALLLLLLL PACKETS PERIODDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
            senderSocket.settimeout(None)
            break
        moveWindow = 0
        remainingPackets = packetsInWindow
        while moveWindow == 0:
            for packet in remainingPackets:
                if packet != 0:
                    bytesToSend = packet
                    senderSocket.sendto(bytesToSend, addressPort)
            moveWindow = listenForACK(senderSocket, remainingPackets, timeout, indexOffset)
        if moveWindow == 1:
            windowCounter += 1

def receiveFiles(receiverSocket, receivedPackets, windowSize, windowCounter, timeout):
    indexOffset = windowSize * windowCounter
    receiverSocket.settimeout(timeout)
    while True:
        # if all packets received, move window
        if 0 not in receivedPackets:
            # if all packets including "last file" received, stop the receiver function
            if findLastFile(receivedPackets[len(receivedPackets) - 1]) == 1:
                return -1
            return 1
        # try to receive packets and place them in the appropriate window
        try:
            receivedPair = receiverSocket.recvfrom(bufferSize)
            receivedPacket = receivedPair[0]
            address = receivedPair[1]
            bytesToSend = createByteCode(3, findClient(receivedPacket), findPartNum(receivedPacket), findfileNameNum(receivedPacket), 0)
            receiverSocket.sendto(bytesToSend, address)
            if (findPartNum(receivedPacket) - indexOffset) < (indexOffset + windowSize):
                receivedPackets[findPartNum(receivedPacket) - indexOffset] = receivedPacket
        # if packet not received, do not move the window
        except:
            return 0
            


# takes in receiver socket and the address port of the sender, along with the first packet
def selectiveARQReceiver(receiverSocket, addressPort, firstPacket):
    windowSize = findWindowSize(firstPacket)
    windowCounter = 0
    timeout = windowSize*8
    indexOffset = windowSize * windowCounter
    totalReceivedPackets = []
    receivedPacketsInWindow = [0]*windowSize
    clientNumber = findClient(firstPacket)
    fileNameNum = findfileNameNum(firstPacket)
    moveWindow = 0
    while True:
        moveWindow = receiveFiles(receiverSocket, receivedPacketsInWindow, windowSize, windowCounter, timeout)
        if moveWindow == -1:
            totalReceivedPackets = totalReceivedPackets + receivedPacketsInWindow
            break
        for packet in range(len(receivedPacketsInWindow)):
            if receivedPacketsInWindow[packet] == 0:
                missingPartNum = packet + indexOffset
                if packet == len(receivedPacketsInWindow):
                    lastNum = 1
                else:
                    lastNum = 0
                bytesToSend = createByteCode(4, clientNumber, missingPartNum, fileNameNum, lastNum)
                receiverSocket.sendto(bytesToSend, addressPort)
        if moveWindow == 1:
            windowCounter += 1
            totalReceivedPackets = totalReceivedPackets + receivedPacketsInWindow
            moveWindow = 0
            receivedPacketsInWindow = [0]*windowSize
            indexOffset = windowSize * windowCounter
    return totalReceivedPackets



# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
