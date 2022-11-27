# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2

from common import *

# This initialises all of the controllers sockets
ownId = bytes.fromhex(sys.argv[1])
sockets = initialiseSockets(sys.argv, 2)

# This creates the forwarding table and the graph used for creating optimal paths
# The forwarding table is a dictionary of arrays
# Each key is an element ID and the value is an array of the IP addresses of the sockets
# That that element is in control of
forwardingTable = manager.dict()
forwardingTableMutex = manager.Lock()
# The graph is made up of nodes (element IDs) and edges (connections if the 2 nodes share a subnet)
graph = manager.dict()

# This creates an empty node of the element ID
def addNode(networkGraph, node):
    networkGraph[node] = []

# This symmetrically adds an edge between 2 nodes (elements) if they share a subnet
def addEdge(networkGraph, node1, node2):
    currentEdges = networkGraph[node1]
    currentEdges.append(node2)
    networkGraph[node1] = currentEdges
    currentEdges = networkGraph[node2]
    currentEdges.append(node1)
    networkGraph[node2] = currentEdges
        
# This function adds both element IDs (keys) and the IP address value to the forwarding table
# It also creates the appropriate node in the graph if the element ID was not already
# present in the forwarding table
def addAddressToTable(table, id, address):
    if id not in table:
        table[id] = []
        addNode(graph, id)
    # adds the IP address to the table
    currentList = table[id]
    currentList.append(address[0])
    forwardingTable[id] = currentList
    currentList = []

# This function handles any declarations sent to the controller.
# It adds the element/IP address to the forwarding table and
# Then it also adds any new edges to the graph
def declarationHandler(forwardingTable, id, address, graph):
    addAddressToTable(forwardingTable, id, address)
    localForwardingTable = dict(forwardingTable)
    ip = address[0]
    for elementId in localForwardingTable:
        listOfIPs = localForwardingTable[elementId]
        for destIp in listOfIPs:
            if compareSubnet(ip, destIp) & (ip != destIp):
                addEdge(graph, id, elementId)
 
# This function listens for messages sent to the controller
# If the message is a declaration from a non-forwarder (if it is 3 bytes long)
# It will add it to the tables
# If it is a declaration (if it is 4 bytes long) from a forwarder it will add it to the tables
# And also will send back the tables
# If it is any other message (more than 4 bytes long) it will simply send back the tables
def listenAndRespond(sock, forwardingTable, forwardingTableMutex, graph):
    try:
        while True:
            receivedBytes = sock.recvfrom(bufferSize)
            message = receivedBytes[0]
            address = receivedBytes[1]
            if len(message) == 3:
                forwardingTableMutex.acquire()
                declarationHandler(forwardingTable, message, address, graph)
                forwardingTableMutex.release()
            else:
                forwardingTableMutex.acquire()
                if len(message) == 4:
                    declarationHandler(forwardingTable, message[:3], address, graph)
                stringifiedIPTable = str(forwardingTable)
                stringifiedNetworkGraph = str(graph)
                forwardingTableMutex.release()
                stringifiedDicts =  stringifiedIPTable + stringifiedNetworkGraph
                bytesOfDicts = ownId + str.encode(stringifiedDicts)
                sock.sendto(bytesOfDicts, address)
    except:
        print("Sorry, encountered an error in the controller, please try again")
                
# This for loop starts all of the processes for the sockets (except for the last one) and calls the
# listenAndRespond() function. The sleep is necessary as otherwise errors to do with multiprocessing
# are common
for sock in range(0, len(sockets) - 1):
    try:
        time.sleep(0.1)
        process = multiprocessing.Process(target=listenAndRespond, args=[sockets[sock], forwardingTable, forwardingTableMutex, graph])
        process.start()
    except:
        print("Sorry, error occurred in the controller, please restart and try again.")
        continue
# This uses the main process for the last socket. It is necessary as the main process has to be running
# otherwise the other parallel processes are prone to failure and errors.
try:
    time.sleep(0.1)
    listenAndRespond(sockets[len(sockets) - 1], forwardingTable, forwardingTableMutex, graph)
except:
    print("Sorry, error occurred in the controller, please restart and try again.")