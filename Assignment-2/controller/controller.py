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

def compareSubnet(ipAddress1, ipAddress2):
    ipAddress1Split = ipAddress1.split(".", 2)
    subnet1 = ipAddress1Split[0] + "." + ipAddress1Split[1]
    ipAddress2Split = ipAddress2.split(".", 2)
    subnet2 = ipAddress2Split[0] + "." + ipAddress2Split[1]
    return subnet1 == subnet2

#def addAddressToTable(table, tableMutex, id, address):
    

def declarationHandler(forwardingTable, forwardingTableMutex, id, address):
    #addAddressToTable(forwardingTable, forwardingTableMutex, id, address)
    forwardingTableMutex.acquire()
    if id not in forwardingTable:
        forwardingTable[id] = []
        graph.add_node(id)
    # adds the IP address to the table
    forwardingTable[id].append(address[0])
    forwardingTableMutex.release()
    
    for key in forwardingTable:
        print(forwardingTable[key])
    ip = address[0]
    for elementId in forwardingTable:
        listOfIPs = forwardingTable[elementId]
        for destIp in listOfIPs:
            if compareSubnet(ip, destIp):
                graph.add_edge(ip, destIp, 1)
        
def findNextDestination(idDest):
    id = idDest[0:3]
    destination = idDest[3:]  

def listenAndRespond(sock, forwardingTable, forwardingTableMutex):
    while True:
        receivedBytes = sock.recvfrom(bufferSize)
        message = receivedBytes[0]
        address = receivedBytes[1]
        #print("The controller received this message: {}".format(message))
        #print("The elements ip is: {}".format(address))
        if len(message) == 3:
            declarationHandler(forwardingTable, forwardingTableMutex, message, address)
        else:
            findNextDestination(message)
                
for sock in sockets:
    process = multiprocessing.Process(target=listenAndRespond,args=[sock, forwardingTable, forwardingTableMutex])
    process.start()