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
    try:
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
    except:
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
    path = findPath(graph, id, destination)
    nextIp = findConnectingIp(path[0], path[1])
    return nextIp
    

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
                nextIp = findNextDestination(message, graph)
                nextIpBytes = str.encode(nextIp)
                sock.sendto(nextIpBytes, address)
    except:
        print("Sorry, encountered an error, please try again")
                

for sock in range(0, len(sockets) - 1):
    try:
        time.sleep(0.1)
        process = multiprocessing.Process(target=listenAndRespond,args=[sockets[sock], forwardingTable, forwardingTableMutex, graph])
        process.start()
    except:
        time.sleep(0.1)
        process = multiprocessing.Process(target=listenAndRespond,args=[sockets[sock], forwardingTable, forwardingTableMutex, graph])
        process.start()
        print("Process killed")
try:
    time.sleep(0.1)
    listenAndRespond(sockets[len(sockets) - 1], forwardingTable, forwardingTableMutex, graph)
except:
    time.sleep(0.1)
    process = multiprocessing.Process(target=listenAndRespond,args=[sockets[sock], forwardingTable, forwardingTableMutex, graph])
    process.start()
    print("Process killed")