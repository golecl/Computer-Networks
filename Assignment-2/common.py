# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

# This is a file containing multiple imports, functions, and constants which are used
# By most/all of the elements. This could be duplicated in each file and is not necessary
# However, for the sake of space and tidiness it is in one file.

import socket
import sys
import multiprocessing
import time

# Maximum size of a UDP Packet
bufferSize = 65507

# Given all of the arguments of an element, and the index of the first own IP address
# in these arguments, this function initialises all the sockets necessary for that element
# It returns them in a list of sockets
def initialiseSockets(arguments, listStart):
    ipAddresses = []
    for argument in range(listStart, len(arguments)):
        ipAddresses.append(arguments[argument])
    sockets = []
    # creates the sockets necessary
    for ip in ipAddresses:
        UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPSocket.bind((ip, 54321))
        sockets.append(UDPSocket)
    return sockets

# Given 2 IP addresses this function compares the first 2 parts of the addresses
# to determine if they belong to the same subnet
# It returns a boolean
def compareSubnet(ipAddress1, ipAddress2):
    ipAddress1Split = ipAddress1.split(".", 2)
    subnet1 = ipAddress1Split[0] + "." + ipAddress1Split[1]
    ipAddress2Split = ipAddress2.split(".", 2)
    subnet2 = ipAddress2Split[0] + "." + ipAddress2Split[1]
    return subnet1 == subnet2

# Given an IP address and the list of available controller IP addresses this function
# Returns the controller IP that is in the same subnet as the socket
# This is useful for declaring all sockets of an element to the controller
def getControllerAddress(ownIp, controllerAddress):
    for address in controllerAddress:
        if compareSubnet(ownIp, address):
            controllerSocket = (address, 54321)
    return controllerSocket
        
# Given the socket, list of controller IP addresses, and Element ID this function declares the
# socket to the controller      
def declare(sock, controllerAddress, id):
    declaration = id
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp, controllerAddress)
    sock.sendto(declaration, controllerSocket)
    
# Returns the final destination Element ID in bytes when given the whole message
def getFinalId(bytesMessage):
    finalId = bytesMessage[3:6]
    return finalId