# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2
import multiprocessing
from common import *

id = bytes.fromhex(sys.argv[1])
sockets = initialiseSockets(sys.argv, 2)

manager = multiprocessing.Manager()
forwardingTable = manager.dict()
forwardingTableMutex = manager.Lock()
graph = manager.dict()

def addNode(networkGraph, node):
    networkGraph[node] = []

def addEdge(networkGraph, node1, node2):
    currentEdges = networkGraph[node1]
    currentEdges.append(node2)
    networkGraph[node1] = currentEdges
    currentEdges = networkGraph[node2]
    currentEdges.append(node1)
    networkGraph[node2] = currentEdges
    
def findPath(networkGraph, start, end):
    print("This is the starting node: ", start)
    print("This is the ending node: ", end)
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
    print("So sorry, but a connecting path doesn't exist :(")
    return

def findConnectingIp(start, end):
    localForwardingTable = dict(forwardingTable)
    for ip1 in localForwardingTable[start]:
        for ip2 in localForwardingTable[end]:
            if compareSubnet(ip1, ip2):
                return ip2
        
def addAddressToTable(table, id, address):
    if id not in table:
        table[id] = []
        addNode(graph, id)
    # adds the IP address to the table
    currentList = table[id]
    currentList.append(address[0])
    forwardingTable[id] = currentList
    currentList = []

def declarationHandler(forwardingTable, id, address, graph):
    addAddressToTable(forwardingTable, id, address)
    localForwardingTable = dict(forwardingTable)
    ip = address[0]
    for elementId in localForwardingTable:
        listOfIPs = localForwardingTable[elementId]
        for destIp in listOfIPs:
            if compareSubnet(ip, destIp) & (ip != destIp):
                addEdge(graph, id, elementId)
        
def findNextDestination(idDest, graph):
    id = idDest[0:3]
    destination = idDest[3:6]
    print("This is the graph ", graph)
    path = findPath(graph, id, destination)
    print("This is the path ", path)
    nextIp = findConnectingIp(path[0], path[1])
    return nextIp
    

def listenAndRespond(sock, forwardingTable, forwardingTableMutex, graph):
    while True:
        receivedBytes = sock.recvfrom(bufferSize)
        message = receivedBytes[0]
        address = receivedBytes[1]
        print(message)
        if len(message) == 3:
            forwardingTableMutex.acquire()
            declarationHandler(forwardingTable, message, address, graph)
            forwardingTableMutex.release()
        else:
            nextIp = findNextDestination(message, graph)
            nextIpBytes = str.encode(nextIp)
            print("This is the next ip ", nextIpBytes)
            sock.sendto(nextIpBytes, address)
                

for sock in range(0, len(sockets) - 1):
    process = multiprocessing.Process(target=listenAndRespond,args=[sockets[sock], forwardingTable, forwardingTableMutex, graph])
    process.start()
listenAndRespond(sockets[len(sockets) - 1], forwardingTable, forwardingTableMutex, graph)