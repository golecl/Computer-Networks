# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

# This initial block of code initialies all variables and sockets
# It gets all of the IP information from the arguments passed into it
id = bytes.fromhex(sys.argv[1])
controllerAddress = []
controllerAddress.append(sys.argv[2])
controllerAddress.append(sys.argv[3])
sockets = initialiseSockets(sys.argv, 4)  

forwardingTable = manager.dict()
forwardingTableMutex = manager.Lock()
# The graph is made up of nodes (element IDs) and edges (connections if the 2 nodes share a subnet)
graph = manager.dict()
 
time.sleep(3)    

# Declares a forwarder, gets the current ip table and network graph from the controller and updates it
def declareForwarder(sock, controllerAddress, id, managerIpTable, managerNetworkGraph):
    declaration = id + bytes.fromhex("FF")
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp, controllerAddress)
    sock.sendto(declaration, controllerSocket)
    receviedBytes = sock.recvfrom(bufferSize)[0]
    stringOfDicts = receviedBytes[3:].decode()
    destringifyDicts(stringOfDicts, managerIpTable, managerNetworkGraph)
    
# When given a string containing two dictionaries, it updates the IP table and Network Graph to those 
# dictionaries
def destringifyDicts(stringDicts, managerIpTable, managerNetworkGraph):
    stringIPTable = stringDicts.split('}')[0] + '}'
    stringNetworkGraph = stringDicts.split('}')[1] + '}'
    managerIpTable.clear()
    managerIpTable.update(ast.literal_eval(stringIPTable))
    managerNetworkGraph.clear()
    managerNetworkGraph.update(ast.literal_eval(stringNetworkGraph))

# This finds the most optimal path between the given starting element ID (the id of the
# current forwarder, not the original user origin ID) and returns the path
# as an array of element IDs
def findPath(networkGraph, start, end):
    explored = []
    queue = [[start]]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in explored:
            neighbours = networkGraph[node]
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                if neighbour == end:
                    return new_path
            explored.append(node)
    
# This function finds the IP address that a forwarder should send to when given the
# starting node and the destination node
def findConnectingIp(start, end):
    localForwardingTable = dict(forwardingTable)
    for ip1 in localForwardingTable[start]:
        for ip2 in localForwardingTable[end]:
            if compareSubnet(ip1, ip2):
                return ip2

# This function, given the header, calls the functions findPath() and findConnectingIp()
# and returns the next IP address that the forwarder should send the packet to       
def findNextDestination(header, graph):
    try:
        id = header[0:3]
        destination = header[3:6]
        localGraph = dict(graph)
        path = findPath(localGraph, id, destination)
        nextIp = findConnectingIp(path[0], path[1])
        return nextIp
    except:
        return

# Returns the correct socket to send from when given the IP address to send to.
def chooseSocket(listOfSockets, nextIpAddress):
    for sock in listOfSockets:
        socketsIP = sock.getsockname()[0]
        if compareSubnet(socketsIP, nextIpAddress[0]):
            return sock
    return

# This function forwards any message it receives, it calls all necessary functions
# And sends the message to the correct IP
def forward(sock, message, forwardingTable, forwardingTableMutex, graph):
    print("The user {} wants to send this message: {}".format(message[0:3].hex().upper(), message))
    nextAddress = (None, 54321)
    while nextAddress[0] == None:
        nextAddress = getForwardingAddress(sock, message, forwardingTable, forwardingTableMutex, graph)
    correctSocket = chooseSocket(sockets, nextAddress)
    print("Received at socket {}".format(sock.getsockname()[0]))
    print("Using socket with IP {} to send to {}\n".format(correctSocket.getsockname()[0], nextAddress[0]))
    correctSocket.sendto(message, nextAddress)

# This function sends a request to the controller asking for the latest version
# Of the IP table and the Forwarding Graph. It then updates both of the local tables
# Or tries to forward a message if the message it received was not from the controller
def updateTables(sock, bytesMessage, forwardingTable, forwardingTableMutex, graph):
    print("Requesting an updated forwarding table!")
    finalId = getFinalId(bytesMessage)
    header = id + finalId
    currentIp = sock.getsockname()[0]
    controllerSocket = getControllerAddress(currentIp, controllerAddress)
    sock.sendto(header, controllerSocket)
    bytesOfDicts = sock.recvfrom(bufferSize)[0]
    if bytesOfDicts[:3] == bytes.fromhex("C0C0C0"):
        stringifiedDicts = bytesOfDicts[3:].decode()
        forwardingTableMutex.acquire()
        destringifyDicts(stringifiedDicts, forwardingTable, graph)
        forwardingTableMutex.release()
    else:
        message = bytesOfDicts[0]
        forward(sock, message, forwardingTable, forwardingTableMutex, graph)

# This function tries to find the next destination or updates the tables if a destination does not exist
def getForwardingAddress(sock, bytesMessage, forwardingTable, forwardingTableMutex, graph):
    try:
        finalId = getFinalId(bytesMessage)
        header = id + finalId
        nextAddressString = findNextDestination(header, graph)
        if nextAddressString == None:
            updateTables(sock, bytesMessage, forwardingTable, forwardingTableMutex, graph)
        nextAddress = (nextAddressString, 54321)
        return nextAddress
    except:
        print("Something went wrong at the forwarder, please try again")
        return (None, 54321)

# This function continuously waits for a message, it then asks the controller where it should
# Send it to. It then sends it to that address from the appropriate socket. (It uses the compareSubnets
# function to determine which socket it should send it to)
def listenAndForward(sock, forwardingTable, forwardingTableMutex, graph):
    try:
        while True:
            receivedBytes = sock.recvfrom(bufferSize)
            message = receivedBytes[0]
            forward(sock, message, forwardingTable, forwardingTableMutex, graph)
    except:
        print("Sorry, encountered an error in the forwarder, please restart and try again")
        listenAndForward(sock, forwardingTable, forwardingTableMutex, graph)

print("Forwarder {} is up".format(id.hex().upper()))

# This block of code declares both of the sockets in the forwarder
# It then starts a multiprocess for one of the sockets and then also starts a main process
# For the other socket, this is because without a main process the multiprocessing encounters
# Lots of errors
forwardingTableMutex.acquire()
declareForwarder(sockets[0], controllerAddress, id, forwardingTable, graph)
forwardingTableMutex.release()
forwardingTableMutex.acquire()
declareForwarder(sockets[1], controllerAddress, id, forwardingTable, graph)
forwardingTableMutex.release()
process = multiprocessing.Process(target=listenAndForward,args=[sockets[0], forwardingTable, forwardingTableMutex, graph])
process.start()
listenAndForward(sockets[1], forwardingTable, forwardingTableMutex, graph)