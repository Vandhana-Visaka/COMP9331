#Written by Vandhana Visakamurthy for COMP9331
#Linked State Routing Algorithm
#Assignment COMP9331
#zID : z5222191
import os
import sys
from socket import *
import random
import time
import threading
from datetime import datetime
filename = sys.argv[1]
#x = sys.argv[2]
#y = sys.argv[3]
file = open(filename,'r')
content = file.read()
file.close()
clean=[]
for n in content.splitlines():
    clean.append(n)
print(clean)
router_id = clean[0].split()[0]
router_port = int(clean[0].split()[1])
no_of_neighbours = int(clean[1])
#printing the router details
print(f'Router ID : {router_id}')
print(f'Router Port : {router_port}')
print(f'Number of Neighbours : {no_of_neighbours}')
#details of the neighbours are stored in the neighbours list as list of lists
neighbours = []
for n in range(2,2 + no_of_neighbours):
    temp = []
    for i in clean[n].split():
        temp.append(i)
    neighbours.append(temp)
#print(neighbours)
#source dictionary
origin = {}
for n in neighbours:
    origin[n[0]] = n[1]
#converting the cost into float and port numbers as int for calculations
for n in neighbours:
    for index,value in enumerate(n):
        if index==1:
            n[index] = float(value)
        elif index==2:
            n[index] = int(value)
#storing the port numbers alone in a list
neighbour_ports = []
for n in neighbours:
    neighbour_ports.append(n[2])
#print(neighbour_ports)
topology = {}
packet_copy = {}
status = {}
topology[router_id] = origin
sequences = []
LSA = ' '.join(clean)
#function to process the received packets and update the routing table
def packet_processing(packet):
    global sequences
    global topology
    processed =[]
    for n in packet.split():
        processed.append(n)
    #print(processed)
    source = processed[1]
    sequence_no = int(processed[0])
    loop = int(processed[3])
    dict = {}
    for n in range(4,len(processed),3):
        #temp=[]
        dict[processed[n]] = float((processed[n+1]))
        #print(temp)
    if sequence_no not in sequences:
        topology[source] = dict
        sequences.append(sequence_no)
        #print(topology)
        return topology
    #else:
        #print(sequence_no)

#socket initialisation
s = socket(AF_INET,SOCK_DGRAM)
s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
s.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
c = socket(AF_INET,SOCK_DGRAM)
c.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
c.bind(('',router_port))
#function to send Heartbeat messages
def Heartbeats(router_id,router_port,neighbour_ports):
    #time.sleep(0.5)
    now = datetime.now()
    time_stamp = datetime.timestamp(now)
    message = str(router_id) + ' ' + str(time_stamp)
    for n in neighbour_ports:
        if n!=router_port:
            s.sendto(message.encode(),('localhost',n))

#function to sennd packets

def sendMessages(router_port,neighbour_ports,LSA):
    seq_no = random.randrange(10000,99999)
    message = str(seq_no) + ' ' + LSA
    #time.sleep(1)
    for n in neighbour_ports:
        if n!=router_port:
            s.sendto(message.encode(),('localhost',n))

#function to receive and decode the heartbeat sendMessages
# def receiveHeartbeats(heartbeat):
#     global packet_copy
#     status = {}
#     if heartbeat in status:
#         status[heartbeat]+=1
#     else:
#         status[heartbeat]=1
#     print(status)
#     print(f'packet copy : {packet_copy}')

#function to receive packets
last_updated = []
def Delete(delete_node,graph):
    for n in graph:
        if delete_node in graph[n]:
            del graph[n][delete_node]
    if delete_node in graph:
         del graph[delete_node]
    return graph

#rejoined nodes are checked using a function
#if the last timestamp of the router in status is the same as the one when it was declared dead
#then it is dead
#otherwise the topology will be updated using the local cache of the topology

def receiveMessages(router_id,client,neighbours):
    global topology
    global sequences
    global packet_copy
    global status
    global last_updated
    dead_nodes = []
    data,addr = client.recvfrom(1024)
    temp = data.decode()
    #print(temp)
    first = str(temp.split()[0])
    #Dijkstra(x,y,z)
    #new_LSA = ' '.join(list(temp.split())[1:])
    #sendMessages(source_port,neighbour_ports,new_LSA)
    if len(first)==1:
        #receiveHeartbeats(temp)
        print(f'heartbeat:{first}')
        stamp = float(temp.split()[1])
        now = datetime.now()
        current_time = datetime.timestamp(now)
        difference = current_time - stamp
        last_updated.append(difference)
        status[first] = last_updated
        #print(f'difference : {difference}')
        if len(last_updated)>1:
            #print(status[first])
            if(difference - status[first][-2])>8:
                for n in neighbour_ports:
                    code = 'DEAD ROUTER' + ' ' + str(first)
                    if n!=router_port:
                        s.sendto(code.encode(),('localhost',n))
            last_updated.pop(0)
            status[first] = last_updated
        else:
            last_updated.append(difference - difference)
        # if temp in status:
        #     status[temp] += 1
        # else:
        #     status[temp] = 1
        # print(status)
        # max_value,max_key = max((value,key) for key,value in status.items())
        # min_value,min_key = min((value,key) for key,value in status.items())
        # if max_value - min_value > 15:
        #     dead_nodes.append(min_key)
        # for n in dead_nodes:
        #     code = 'DEAD ROUTER' + ' ' + str(n)
        #     s.sendto(temp.encode(),('localhost',n))
    elif first == 'DEAD':
        print(f'DEAD : {temp}')
        dead_node = temp.split()[2]
        topology_copy = topology.copy()
        new_topology = Delete(dead_node,topology_copy)
        print(f'new_topology:{new_topology}')
        topology = new_topology
        dead_nodes.append(dead_node)
        for n in neighbour_ports:
            if n!=router_port:
                s.sendto(temp.encode(),('localhost',n))
    else:
        source_port = int(temp.split()[2])
        # source_id = str(temp.split()[1])
        # packet_copy[source_id] = temp
        # print(f'packets : {packet_copy}')
        packet_processing(temp)
        # if source_id in status:
        #     status[source_id]+=1
        # else:
        #     status[source_id]=1
        #print(f'status : {status}')
        for n in neighbour_ports:
            if n!=router_port and n!=source_port:
                s.sendto(temp.encode(),('localhost',n))

def Dijkstra(start,stop,network):
    #print(f'start net : {network}')
    #global topology
    distance = {}
    infinity = 999
    graph = network.copy()
    previous = {}

    #if a node exists in a graph initialize the ditance to infinity if not start node
    for node in graph:
        #print(node)
        distance[node] = infinity
    #if the node is the start node then distance from start to start is 0
    distance[start] = 0
    #x = ''
    while graph: #checking if dictionary is empty or not
        shortest = None
        for node in graph:
            #check if the node is null and if null initialize the value as node value
            if shortest is None:
                shortest = node
            #check if distance to the node is lesser than the shortest distance to the node
            elif distance[node] < distance[shortest]:
                #if it is lesser, then the new shortest path is the distance to the node
                shortest = node
        #print(graph[shortest])
    #accessing key,value in a dictionary of dictionary using items
        for next,weight in graph[shortest].items():
            #check if sum of weight and the distance to the shortest is lesser than distance to the next node
            #print(weight)
            if float(weight) + float(distance[shortest]) < float(distance[next]):
                #assign the distance to the next node as sum of weight to the next node and distance upto the current node
                distance[next] = float(weight) + float(distance[shortest])
                #print(next,distance[next])
                #previous keeps track of the path
                previous[next] = shortest
                #print(previous[next])
                #x += previous[next]
        graph.pop(shortest)
        #print(f'x:{x}')
    path = ''
    present = stop
    while present != start:
        path = path + present
        present = previous[present]
    path = path + start
    temp = path[::-1]
    path = temp
    #print(f'start:{start}')
    #print(f'end:{stop}')
    if distance[stop] != infinity:
        return path,distance[stop]
        #print(f'network : {network}')
counter = 0
def shortestPath(neighbours,counter,router_id):
    global topology
    nodes = []
    distances = []
    for n in topology:
        nodes.append(n)
    if counter > 70:
        for n in nodes:
            current_end = n
            if current_end != router_id:
                path,distance = Dijkstra(router_id,current_end,topology)
                distances.append((current_end,path,distance))
                    #print(topology)
    elif counter > 71:
        #time.sleep(30)
        for n in nodes:
            current_end = n
            if current_end != router_id:
                path,distance = Dijkstra(router_id,current_end,topology)
                distances.append((current_end,path,distance))
    #time.sleep(30)
    # elif counter > 21:
    #     time.sleep(30)
    #     for n in nodes:
    #         current_end = n
    #         if current_end != router_id:
    #             path,distance = Dijkstra(router_id,current_end,topology)
    #             distances.append((current_end,path,distance))
    #printing output
    if distances:
        print(f'I am Router {router_id}.')
        for n in distances:
            print(f'Least cost path to router {n[0]} : {n[1]} and the cost is {n[2]}.')

def running():
    global counter
    while True:
        time.sleep(1)
        counter+=1
        Heartbeats(router_id,router_port,neighbour_ports)
        sendMessages(router_port,neighbour_ports,LSA)
        receiveMessages(router_id,c,neighbours)
        #print(f'topology : {topology}')
        shortestPath(neighbours,counter,router_id)
        #print(f'topology : {topology}')
    #except KeyError:
        #pass
#Main function to keep track of all the running threads
if __name__=='__main__':
    thread1 = threading.Thread(target = sendMessages(router_port,neighbour_ports,LSA))
    thread2 = threading.Thread(target = receiveMessages(router_id,c,neighbours))
    thread3 = threading.Thread(target = shortestPath(neighbours,counter,router_id))
    thread4 = threading.Thread(target = Heartbeats(router_id,router_port,neighbour_ports))
    thread5 = threading.Thread(target = running())
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    #thread5.join()
