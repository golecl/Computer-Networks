# CODE WRITTEN BY LAURA GOLEC FOR CSU33031 ASSIGNMENT 2
from dijkstar import Graph, find_path
import multiprocessing
from common import *

id = bytes.fromhex(sys.argv[1])
sockets = initialiseSockets(sys.argv, 2)

graph = Graph()

manager = multiprocessing.Manager()
forwardingTable = manager.dict()
forwardingTableMutex = manager.Lock()

def addAddressToTable(table, id, address):
    if id not in table:
        table[id] = []
        graph.add_node(id)
    # adds the IP address to the table
    currentList = table[id]
    currentList.append(address[0])
    forwardingTable[id] = currentList
    currentList = []

def declarationHandler(forwardingTable, id, address):
    addAddressToTable(forwardingTable, id, address)
    localForwardingTable = dict(forwardingTable)
    print(localForwardingTable)
    ip = address[0]
    for elementId in localForwardingTable:
        listOfIPs = localForwardingTable[elementId]
        #print(listOfIPs)
        for destIp in listOfIPs:
            if compareSubnet(ip, destIp):
                graph.add_edge(ip, destIp, 1)
        
def findNextDestination(idDest):
    id = idDest[0:3]
    #print(id)
    destination = idDest[3:6]
    #print(destination)
    print(graph)
    path = find_path(graph, id, destination)
    print(path)
    #except:
        #print("sorry, no path")

def listenAndRespond(sock, forwardingTable, forwardingTableMutex):
    while True:
        receivedBytes = sock.recvfrom(bufferSize)
        message = receivedBytes[0]
        address = receivedBytes[1]
        if len(message) == 3:
            forwardingTableMutex.acquire()
            declarationHandler(forwardingTable, message, address)
            forwardingTableMutex.release()
        else:
            findNextDestination(message)
                

for sock in range(0, len(sockets) - 1):
    process = multiprocessing.Process(target=listenAndRespond,args=[sockets[sock], forwardingTable, forwardingTableMutex])
    process.start()
listenAndRespond(sockets[len(sockets)-1], forwardingTable, forwardingTableMutex)