import multiprocessing
from random import randrange
from shutil import move
import socket
import random
import math
from listOfFiles import *
from func_timeout import func_timeout, FunctionTimedOut

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

def listenForACK(socketName, packetsToSendBack):
    print("i exist 2")
    packetsLeft = 0
    for x in packetsToSendBack:
        if x != 0:
            packetsLeft += 1
    print("i exist 3")
    while True:
        print("i exist 4")
        print(socketName)
        bytesReceived = socketName.recvfrom(bufferSize)
        print("i exist 5")
        bytesMessage = bytesReceived[0]
        byteCode = getByteCodeFromMessage(bytesMessage)
        operation = findCode(byteCode)
        print("i exist")
        if operation == 3:
            partNum = findPartNum(byteCode)
            packetsToSendBack[partNum] = 0
            packetsLeft -= 1
            print("got ACK for packet ", partNum)
        elif operation == 4:
            partNum = findPartNum(byteCode)
            packetsToSendBack[partNum] = bytesMessage
            packetsLeft += 1
            print("got NACK for packet ", partNum)
        if packetsLeft == 0:
            return True

# takes in sender socket, the address port of the reciever and the packets to send
def selectiveARQSender(senderSocket, addressPort, packetsToSend):
    windowSize = findWindowSize(packetsToSend[0])
    print("window size sender = ", windowSize)
    print("got here 3")
    windowCounter = 0
    timeout = windowSize*2
    while True:
        try:
            packetsInWindow = packetsToSend[windowCounter*windowSize : (windowCounter + 1)*windowSize]
            print("got here 4")
        except:
            break
        moveWindow = False
        remainingPackets = packetsInWindow
        while moveWindow == False:
            print("got here 5")
            for packet in remainingPackets:
                if packet != 0:
                    bytesToSend = packet
                    print("sending packet number ", findPartNum(bytesToSend))
                    senderSocket.sendto(bytesToSend, addressPort)
                    print("got here 6")
            try:
                moveWindow = func_timeout(timeout, listenForACK, args=(senderSocket, remainingPackets))
            except FunctionTimedOut:
                print("got here 7")
                moveWindow = False
        if moveWindow == True:
            windowCounter += 1

def receiveFiles(receiverSocket, receivedPackets, windowSize, windowCounter):
    indexOffset = windowSize * windowCounter
    while True:
        if 0 not in receivedPackets:
            if findLastFile(receivedPackets[len(receivedPackets) - 1]) == 1:
                return -1
            return True
        receivedPacket = receiverSocket.recvfrom(bufferSize)
        receivedPackets.insert(findPartNum(receivedPacket) - indexOffset, receivedPacket)


# takes in receiver socket and the address port of the sender, along with the first packet
def selectiveARQReceiver(receiverSocket, addressPort, firstPacket):
    windowSize = findWindowSize(firstPacket)
    print("window size receiver = ", windowSize)
    print("got here 8")
    windowCounter = 0
    timeout = windowSize*2
    totalReceivedPackets = []
    receivedPacketsInWindow = [0]*windowSize
    receivedPacketsInWindow.insert(findPartNum(firstPacket), firstPacket)
    moveWindow = False
    while True:
        print("got here 9")
        windowOffset = windowSize * windowCounter
        try:
            moveWindow = func_timeout(timeout, receiveFiles, args=(receiverSocket, receivedPacketsInWindow, windowSize, windowCounter))
            print(moveWindow)
            if moveWindow == -1:
                print("got here 10")
                break
        except FunctionTimedOut:
            for packet in range(len(receivedPacketsInWindow)):
                if receivedPacketsInWindow[packet] == 0:
                    print("got here 11")
                    missingPartNum = packet + windowOffset
                    if packet == len(receivedPacketsInWindow):
                        lastNum = 1
                    else:
                        lastNum = 0
                    bytesToSend = createByteCode(4, findClient(firstPacket), missingPartNum, findfileNameNum(firstPacket), lastNum)
                    print("missing part ", missingPartNum)
                    print("this is what im sending ", bytesToSend, addressPort)
                    receiverSocket.sendto(bytesToSend, addressPort)
                    print("got here 12")
        if moveWindow == True:
            windowCounter += 1
            totalReceivedPackets = totalReceivedPackets + receivedPacketsInWindow
            print("got here 13")
    return totalReceivedPackets



# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
