import socket
import sys
from threading import Thread
from threading import Lock

import time
import hashlib
import struct
import threading


#Assign port numbers for Experiment 2
receivePorts = [20,60]
sendPorts=[30,70]
#Initialize sockets for experiment 2
receiverSockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(2)]

senderSockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(2)]

for i in range(2):
    receive_address = ('', receivePorts[i])
    receiverSockets[i].bind(receive_address)

threadNumber=1
#R1 and R2 addresses for experiment2
sendingAdresses=["10.10.4.1","10.10.5.1"]
#Create file
file = open("input2.txt", "a+")


#Assign porn information for experiment 1
receivePort = 50
sendPort=60
#Initialize sockets for experiment 1
receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_address = ('', receivePort)
receiverSocket.bind(receive_address)
#R3 address for experiment 1
sendingAdress="10.10.7.2"

#Buffer will keep all file segments
buffer=""
#Current seq number wanted
curr_seq_num=0
#If next current seq numbered packet received, than hold it in next_cur
next_cur=""

generalLock=Lock()


#Read R1 for experiment2
def readSocket1(threadNumber):
    global curr_seq_num,random_time,buffer,next_cur
    send_address0 = (sendingAdresses[0], sendPorts[0])
    send_address1 = (sendingAdresses[1], sendPorts[1])
    while(True):
        try:
            #Check if link is down by timeout exception
            receiverSockets[0].settimeout(15)
            data, address = receiverSockets[0].recvfrom(920)
            if data:
                #If terminate message received break and redirect it to client listeners
                if data=="startTerminationNow1996":
                    for i in range(20):
                        senderSockets[0].sendto("startTerminationNow1996".encode(), send_address0)
                        senderSockets[1].sendto("startTerminationNow1996".encode(), send_address1)
                    print("exited")
                    break
                #Unpack data, seq num and hash
                data_hash = data[:16]
                data_num_struct=data[16:20]
                data_message = data[20:]
                data_num=struct.unpack("i",data_num_struct)
                with generalLock:
                    #Check if corrupted
                    if(hashlib.md5(data_num_struct+data_message).digest() == data_hash ):
                        print("MD5 Correct "+str(data_num)+" curr:"+str(curr_seq_num))
                        #If received packet is current seq number than add it to buffer
                        if(data_num[0]==curr_seq_num):
                            #If next current is not received than just add current seq to buffer and sent Ackt(acknowledment true)
                            if next_cur=="":
                                curr_seq_num+=1
                                ack_message="ACKt".encode()+str(data_num[0])
                                ack_hash=hashlib.md5(ack_message).digest()
                                senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                                senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                                print("Sent ACK "+str(data_num[0]))
                                buffer+=data_message
                            #If next current is received than add it with current to buffer  and sent Ackt(acknowledment true)
                            else:
                                curr_seq_num+=2
                                ack_message="ACKt".encode()+str(data_num[0]+1)
                                ack_hash=hashlib.md5(ack_message).digest()
                                senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                                senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                                print("Sent ACK "+str(data_num[0]+1))
                                buffer+=data_message+next_cur
                                next_cur=""
                        #If next current is received than put it on next_cur  and sent Ackf(acknowledment false)
                        elif(data_num[0]==curr_seq_num+1):
                            ack_message="ACKf".encode()+str(curr_seq_num-1)
                            ack_hash=hashlib.md5(ack_message).digest()
                            senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                            senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                            print("Sent ACK "+str(curr_seq_num-1))
                            next_cur=data_message
                        # Else just sent acknowledment false
                        else:
                            ack_message="ACKf".encode()+str(curr_seq_num-1)
                            ack_hash=hashlib.md5(ack_message).digest()
                            senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                            senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                            print("Sent ACK "+str(curr_seq_num-1))
                    #If data is corrupted than sent ack false
                    else:
                        print("MD5 false")
                        print("Sent ACK "+str(curr_seq_num-1))
                        ack_message="ACKf".encode()+str(curr_seq_num-1)
                        ack_hash=hashlib.md5(ack_message).digest()
                        senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                        senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                        continue
        except:
                #Exception Handling if link1 is down
                print("!!Link1 Down!!")
                break
















#Read R2 for experiment2
def readSocket2(threadNumber):
    global curr_seq_num,random_time,buffer,next_cur
    send_address0 = (sendingAdresses[0], sendPorts[0])
    send_address1 = (sendingAdresses[1], sendPorts[1])
    while(True):
        try:
            #Check if link is down by timeout exception
            receiverSockets[1].settimeout(15)
            data, address = receiverSockets[1].recvfrom(920)
            if data:
                #If terminate message received break and redirect it to client listeners
                if data=="startTerminationNow1996":
                    for i in range(20):
                        senderSockets[1].sendto("startTerminationNow1996".encode(), send_address1)
                        senderSockets[0].sendto("startTerminationNow1996".encode(), send_address0)

                    print("exited")
                    break
                #Unpack data, seq num and hash
                data_hash = data[:16]
                data_num_struct=data[16:20]
                data_message = data[20:]
                data_num=struct.unpack("i",data_num_struct)
                with generalLock:
                    #Check if corrupted
                    if(hashlib.md5(data_num_struct+data_message).digest() == data_hash ):
                        print("MD5 Correct "+str(data_num)+" curr:"+str(curr_seq_num))
                        #If received packet is current seq number than add it to buffer
                        if(data_num[0]==curr_seq_num):
                            #If next current is not received than just add current seq to buffer and sent Ackt(acknowledment true)
                            if next_cur=="":
                                curr_seq_num+=1
                                ack_message="ACKt".encode()+str(data_num[0])
                                ack_hash=hashlib.md5(ack_message).digest()
                                senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                                senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                                print("Sent ACK "+str(data_num[0]))
                                buffer+=data_message
                            #If next current is received than add it with current to buffer  and sent Ackt(acknowledment true)
                            else:
                                curr_seq_num+=2
                                ack_message="ACKt".encode()+str(data_num[0]+1)
                                ack_hash=hashlib.md5(ack_message).digest()
                                senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                                senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                                print("Sent ACK "+str(data_num[0]+1))
                                buffer+=data_message+next_cur
                                next_cur=""
                        #If next current is received than put it on next_cur  and sent Ackf(acknowledment false)
                        elif(data_num[0]==curr_seq_num+1):
                            ack_message="ACKf".encode()+str(curr_seq_num-1)
                            ack_hash=hashlib.md5(ack_message).digest()
                            senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                            senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                            print("Sent ACK "+str(curr_seq_num-1))
                            next_cur=data_message
                        # Else just sent acknowledment false
                        else:
                            ack_message="ACKf".encode()+str(curr_seq_num-1)
                            ack_hash=hashlib.md5(ack_message).digest()
                            senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                            senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                            print("Sent ACK "+str(curr_seq_num-1))
                    #If data is corrupted than sent ack false
                    else:
                        print("MD5 false")
                        print("Sent ACK "+str(curr_seq_num-1))
                        ack_message="ACKf".encode()+str(curr_seq_num-1)
                        ack_hash=hashlib.md5(ack_message).digest()
                        senderSockets[1].sendto(ack_hash+ack_message, send_address1)
                        senderSockets[0].sendto(ack_hash+ack_message, send_address0)
                        continue
        #Exception Handling if link2 is down
        except:
            print("!!Link2 Down!!")
            break;









#Read function for experiment 1
def readSocket(threadNumber):
    global curr_seq_num,random_time,buffer,next_cur
    while(True):
        data, address = receiverSocket.recvfrom(920)
        send_address = (sendingAdress, sendPort)
        if data:
            #If terminate message received break and redirect it to client listeners
            if data=="startTerminationNow1996":
                for i in range(20):
                    senderSocket.sendto("startTerminationNow1996".encode(), send_address)
                print("exited")
                break
            #Unpack data, seq num and hash
            data_hash = data[:16]
            data_num_struct=data[16:20]
            data_message = data[20:]
            data_num=struct.unpack("i",data_num_struct)
            #Check if corrupted
            if(hashlib.md5(data_num_struct+data_message).digest() == data_hash ):
                print("MD5 Correct "+str(data_num)+" curr:"+str(curr_seq_num))
                #If received packet is current seq number than add it to buffer
                if(data_num[0]==curr_seq_num):
                    #If next current is not received than just add current seq to buffer and sent Ackt(acknowledment true)
                    if next_cur=="":
                        curr_seq_num+=1
                        ack_message="ACKt".encode()+str(data_num[0])
                        ack_hash=hashlib.md5(ack_message).digest()
                        senderSocket.sendto(ack_hash+ack_message, send_address)
                        print("Sent ACK "+str(data_num[0]))
                        buffer+=data_message
                    #If next current is received than add it with current to buffer  and sent Ackt(acknowledment true)
                    else:
                        curr_seq_num+=2
                        ack_message="ACKt".encode()+str(data_num[0]+1)
                        ack_hash=hashlib.md5(ack_message).digest()
                        senderSocket.sendto(ack_hash+ack_message, send_address)
                        print("Sent ACK "+str(data_num[0]+1))
                        buffer+=data_message+next_cur
                        next_cur=""
                #If next current is received than put it on next_cur  and sent Ackf(acknowledment false)
                elif(data_num[0]==curr_seq_num+1):
                    ack_message="ACKf".encode()+str(curr_seq_num-1)
                    ack_hash=hashlib.md5(ack_message).digest()
                    senderSocket.sendto(ack_hash+ack_message, send_address)
                    print("Sent ACK "+str(curr_seq_num-1))
                    next_cur=data_message
                # Else just sent acknowledment false
                else:
                    ack_message="ACKf".encode()+str(curr_seq_num-1)
                    ack_hash=hashlib.md5(ack_message).digest()
                    senderSocket.sendto(ack_hash+ack_message, send_address)
                    print("Sent ACK "+str(curr_seq_num-1))
            #If data is corrupted than sent ack false
            else:
                print("MD5 false")
                print("Sent ACK "+str(curr_seq_num-1))
                ack_message="ACKf".encode()+str(curr_seq_num-1)
                ack_hash=hashlib.md5(ack_message).digest()
                senderSocket.sendto(ack_hash+ack_message, send_address)
                continue


#Run experiment 2
if(sys.argv[1]=="2"):
    try:

        #Create threads
        print("Starting exp2")
        threadPool1 = [Thread(target=readSocket1, args=(i,)) for i in range(threadNumber)]
        threadPool2 = [Thread(target=readSocket2, args=(i,)) for i in range(threadNumber)]


        #Start threads
        for thread in threadPool1:
            thread.start()

        for thread in threadPool2:
            thread.start()


        #Join threads
        for thread in threadPool1:
            thread.join()
        for thread in threadPool2:
            thread.join()

        file.write(buffer)
    except:
        print("THREADING ERROR")

#Run experiment 1
else:
    try:
        print("Starting exp1")
        #Create threads
        threadPool = [Thread(target=readSocket, args=(i,)) for i in range(threadNumber)]

        #Start threads
        for thread in threadPool:
            thread.start()

        #Join threads
        for thread in threadPool:
            thread.join()

        senderSocket.close()
        receiverSocket.close()
        file.write(buffer)
    except:
        print("THREADING ERROR")
