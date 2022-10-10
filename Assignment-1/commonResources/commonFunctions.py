import multiprocessing
from random import randrange
import socket
import random
import math
from listOfFiles import *

bufferSize = 65500

# function used to find worker addresses or add them if they do not exist on the list yet
def findIfUnitAlreadyDeclared(list, address):
    # if the unit is already in the list, it returns its index
    try:
        index = list.index(address)
        return index
    # if it is not already on the list it adds it to the end and returns its index
    except:
        list.append(address)
        return list.index(address)

# ~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BYTECODE SECTION ~~~~~~~~~~~~~~~~~~~~~

codeBytes = 1
clientBytes = 2
partNumBytes = 2
fileNameBytes = 2
lastFileBytes = 1
totalHeaderBytes = codeBytes + clientBytes + partNumBytes + fileNameBytes + lastFileBytes

# creates the Byte code used to identify the action, client, current file part, and total file parts
def createByteCode(messageCode, client, partNumber, fileNames, lastFile):
    msgCodeByte = messageCode.to_bytes(codeBytes, 'big') # creates a 8 bit Byte number of the message code
    clientByte = client.to_bytes(clientBytes, 'big') # creates a 16 bit Byte number of the client number
    partNum = partNumber.to_bytes(partNumBytes, 'big') # creates a byte sized number
    fileNameNum = fileNames.to_bytes(fileNameBytes, 'big')
    lastFile = lastFile.to_bytes(lastFileBytes, 'big')
    ByteCode = msgCodeByte + clientByte + partNum + fileNameNum + lastFile
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
    end = start + lastFileBytes
    return int.from_bytes(message[start:end], 'big')

def getStringCodeFromByteCode(byteCode):
    code = findCode(byteCode)
    client = findClient(byteCode)
    partNum = findPartNum(byteCode)
    fileNameNum = findfileNameNum(byteCode)
    lastFile = findLastFile(byteCode)
    string = f'{code:0{codeBytes*8}}' + f'{client:0{clientBytes*8}}' + f'{partNum:0{partNumBytes*8}}' + f'{fileNameNum:0{fileNameBytes*8}}' + f'{lastFile:0{lastFileBytes*8}}'
    return string


# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MULTIPROCESSING SECTION ~~~~~~~~~~~~~~~~~~~~~~~~
