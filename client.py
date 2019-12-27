import socket
import sys
import time
from threading import Lock
from threading import Thread
from threading import Condition
import threading
import hashlib
import struct


# Create  UDP sockets for Exp2
sendPorts =[10,50]
receivePorts=[40,80]

# Create Addresses for Exp2
sendingAdresses=["10.10.1.2","10.10.2.1"]

#Thread number is 1 for both of experiments
threadNumber = 1
#Initialize exp2 sockets
senderSockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(2)]
receiverSockets =[ socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(2)]
for i in range(2):
    receive_address = ('', receivePorts[i])
    receiverSockets[i].bind(receive_address)

#Open Input File
file = open("input.txt", "r")


#Chunk the total file into segments
file_chunks=[]

#Windows size is 6 as we take >
window_size=5

#Current sequence number to sent next
curr_seq_num=0
curr_seq_numLock=Lock()
#Base is the first non acknowledged segment
base=0
baseCon=Condition()


timerLock=Lock()

#EstimatedRTT and deRTT will be used for timeout interval
estimatedRTT=0.2
deRTT=0

#Bools for determining if link1(r1) or link2(r2) are down for exp2
linkDown1=False
linkDown2=False


#Socket Information for experiment 1
sendPort = 40
receivePort = 70
sendingAdress="10.10.3.2"

#Initialize exp1 sockets
senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_address = ('', receivePort)
receiverSocket.bind(receive_address)






#Read file and create Chunks of 900 bytes
def createChunks():
    while(True):
        read_data = file.read(900)
        if not read_data:
            break
        file_chunks.append(read_data)

#This function makes the current sequence number(the sequence to send next) equal to base,
#By doing that it will resend the non acknowledged segment in first sent
def timerHandler():
    global curr_seq_num
    with curr_seq_numLock:
        curr_seq_num=base
    with baseCon:
        baseCon.notify()
    print("TIMER IS CALLED")
    return

#Calculate the new estimatedRTT value. Equation is same as in the book
def timeIntervalFind(SampleRTT):
	global estimatedRTT , deRTT
	estimatedRTT= (0.875 * estimatedRTT) + (0.125 *SampleRTT)
	deRTT= (0.75 *deRTT) + (0.75*abs(SampleRTT - estimatedRTT))
	return estimatedRTT + (4*deRTT)


#Sender function for experiment 2
def sendSocket1(threadNumber):
    global curr_seq_num,timer,startTime
    send_address0 = (sendingAdresses[0], sendPorts[0])
    send_address1 = (sendingAdresses[1], sendPorts[1])
    #Starttime is the sent time of first packet
    startTime=time.time()
    while(True):
        #If Base bigger than file than break
        if base>=len(file_chunks):
            break
        #Check if the curr_seq_num bigger than base plus context window
        with baseCon:
            while curr_seq_num > base+window_size:
                baseCon.wait()
        #If curr sequence equals to base start timer again
        with timerLock:
            if curr_seq_num==base:
                timer=threading.Timer(estimatedRTT,timerHandler)
                timer.start()
        #check if current seq num bigger than file size
        if curr_seq_num>=len(file_chunks):
            if base>=len(file_chunks):
                break
            else:
                curr_seq_num=base
                time.sleep(0.01)
        #Get the current segment
        with curr_seq_numLock:
            try:
                data=file_chunks[curr_seq_num]
            except:
                break
            #Add sequence number and md5 kripto
            data_num=struct.pack("i",curr_seq_num)
            data_hash = hashlib.md5(data_num+data).digest()
            data_total = data_hash +data_num+ data
        #Check the links
        if linkDown1==False and linkDown2==False:
            senderSockets[0].sendto(data_total, send_address0)
            senderSockets[1].sendto(data_total, send_address1)
        elif linkDown1==False:
            senderSockets[0].sendto(data_total, send_address0)
            senderSockets[0].sendto(data_total, send_address0)
        elif linkDown2==False:
            senderSockets[1].sendto(data_total, send_address1)
            senderSockets[1].sendto(data_total, send_address1)
        #Increment current seq number
        with curr_seq_numLock:
            print("Sent with seq="+str(curr_seq_num)+" "+str(struct.unpack("i",data_num))+" base="+str(base)+"  " +str(linkDown1)+" "+str(linkDown2))
            curr_seq_num+=1
        #Sleep for a while
        time.sleep(0.01)
    #Sent Terminate message
    for i in range(30):
        senderSockets[0].sendto("startTerminationNow1996", send_address0)
        senderSockets[1].sendto("startTerminationNow1996", send_address1)


#Read R1 for experiment 2
def readSocket1(threadNumber):
    global base,timer,endTime,curr_seq_num,linkDown1
    #Take the first sample to calculate sampleRtt
    sample_begin=time.time()
    while(True):
        #If not received for 15 sec send exception
        receiverSockets[0].settimeout(15)
        try:
            #Receive from r1
            data, address = receiverSockets[0].recvfrom(1016)
            #Break if termination received
            if data:
                if(data=="startTerminationNow1996"):
                    endTime=time.time()
                    break
                else:
                    #Check if ack corrupted
                    data_hash = data[:16]
                    data_message=data[16:]
                    if(hashlib.md5(data_message).digest() == data_hash ):
                        if data_message[0:3]=="ACK":
                            #Get Ack seq number
                            data_ack_num=int(data_message[4:])
                            #If acknowledged seq bigger than base than update base
                            with baseCon:
                                if data_ack_num+1>base:
                                    base=data_ack_num+1
                                    baseCon.notify()
                            with timerLock:
                                    #If the acknowledged number is the expected number of server than reset the timer
                                    # also recalculate estimatedRTT
                                    if data_message[3]=="t":
                                        sample_end=time.time()
                                        timeIntervalFind(sample_end-sample_begin)
                                        sample_begin=sample_end
                                        timer.cancel()
                                        timer=threading.Timer(estimatedRTT,timerHandler)
                                        timer.start()
                            print("Received ACK"+str(data_ack_num))

                    else:
                        #If ack is corrupted notify baseCon
                        with baseCon:
                            baseCon.notify()
                        print("NOT RECEIVED ACK")
        except:
            #If link is down then handle exception
            print("!!Link1 Down!!")
            linkDown1=True;
            break;

#Read R2 for experiment 2
def readSocket2(threadNumber):
    global base,timer,endTime,curr_seq_num,linkDown2
    #Take the first sample to calculate sampleRtt
    sample_begin=time.time()
    while(True):
        #If not received for 15 sec send exception
        receiverSockets[1].settimeout(15)
        try:
            #Receive from r2
            data, address = receiverSockets[1].recvfrom(1016)
            #Break if termination received
            if data:
                if(data=="startTerminationNow1996"):
                    endTime=time.time()
                    break
                else:
                    #Check if ack corrupted
                    data_hash = data[:16]
                    data_message=data[16:]
                    if(hashlib.md5(data_message).digest() == data_hash ):
                        if data_message[0:3]=="ACK":
                            #Get Ack seq number
                            data_ack_num=int(data_message[4:])
                            #If acknowledged seq bigger than base than update base
                            with baseCon:
                                if data_ack_num+1>base:
                                    base=data_ack_num+1
                                    baseCon.notify()
                            with timerLock:
                                    #If the acknowledged number is the expected number of server than reset the timer
                                    # also recalculate estimatedRTT
                                    if data_message[3]=="t":
                                        sample_end=time.time()
                                        timeIntervalFind(sample_end-sample_begin)
                                        sample_begin=sample_end
                                        timer.cancel()
                                        timer=threading.Timer(estimatedRTT,timerHandler)
                                        timer.start()
                            print("Received ACK"+str(data_ack_num))

                    else:
                        #If ack is corrupted notify baseCon
                        with baseCon:
                            baseCon.notify()
                        print("NOT RECEIVED ACK")
        except:
            #If link is down then handle exception
            print("!!Link2 Down!!")
            linkDown2=True;
            break;













#Sender function for experiment 1
def sendSocket(threadNumber):
    global curr_seq_num,timer,startTime
    send_address = (sendingAdress, sendPort)
    #Starttime is the sent time of first packet
    startTime=time.time()
    while(True):
        #If Base bigger than file than break
        if base>=len(file_chunks):
            break
        #Check if the curr_seq_num bigger than base plus context window
        with baseCon:
            while curr_seq_num > base+window_size:
                baseCon.wait()
        #If curr sequence equals to base start timer again
        with timerLock:
            if curr_seq_num==base:
                timer=threading.Timer(estimatedRTT,timerHandler)
                timer.start()
        #check if current seq num bigger than file size
        with curr_seq_numLock:
            if curr_seq_num>=len(file_chunks):
                if base>=len(file_chunks):
                    break
                else:
                    curr_seq_num=base
            #Get the current segment
            data=file_chunks[curr_seq_num]
            data_num=struct.pack("i",curr_seq_num)
            #Add sequence number and md5 kripto
            data_hash = hashlib.md5(data_num+data).digest()
            data_total = data_hash +data_num+ data
        #If current sequence equals to base than send twice for insure it
        if curr_seq_num==base:
            senderSocket.sendto(data_total, send_address)
            senderSocket.sendto(data_total, send_address)
        else:
            senderSocket.sendto(data_total, send_address)
        with curr_seq_numLock:
            print("Sent with seq="+str(curr_seq_num)+" "+str(struct.unpack("i",data_num))+" base="+str(base))
            curr_seq_num+=1
        #Sleep for a while
        time.sleep(0.01)
    #Send termination
    for i in range(30):
        senderSocket.sendto("startTerminationNow1996", send_address)



#Read R3 for experiment 1
def readSocket(threadNumber):
    global base,timer,endTime,curr_seq_num
    #Take the first sample to calculate sampleRtt
    sample_begin=time.time()
    while(True):
        #Receive from r3
        data, address = receiverSocket.recvfrom(1016)
        if data:
            #Break if termination received
            if(data=="startTerminationNow1996"):
                endTime=time.time()
                break
            else:
                data_hash = data[:16]
                data_message=data[16:]
                #Check if ack corrupted
                if(hashlib.md5(data_message).digest() == data_hash ):
                    if data_message[0:3]=="ACK":
                        #Get Ack seq number
                        data_ack_num=int(data_message[4:])
                        with baseCon:
                            #If acknowledged seq bigger than base than update base
                            if data_ack_num+1>base:
                                base=data_ack_num+1
                                baseCon.notify()
                        with timerLock:
                                #If the acknowledged number is the expected number of server than reset the timer
                                # also recalculate estimatedRTT
                                if data_message[3]=="t":
                                    sample_end=time.time()
                                    timeIntervalFind(sample_end-sample_begin)
                                    sample_begin=sample_end
                                    timer.cancel()
                                    timer=threading.Timer(estimatedRTT,timerHandler)
                                    timer.start()


                        print("Received ACK"+str(data_ack_num))

                else:
                    with baseCon:
                        baseCon.notify()
                    print("NOT RECEIVED ACK")


#If experiment 2 called
if(sys.argv[1]=="2"):
            print("Starting exp2")
            createChunks()
            threadPoolClient = [Thread(target=sendSocket1, args=(i,)) for i in range(threadNumber)]
            threadPoolServer1 = [Thread(target=readSocket1, args=(i,)) for i in range(threadNumber)]
            threadPoolServer2 = [Thread(target=readSocket2, args=(i,)) for i in range(threadNumber)]

            for thread in threadPoolClient:
                thread.start()

            for thread in threadPoolServer1:
                thread.start()

            for thread in threadPoolServer2:
                thread.start()

            for thread in threadPoolServer1:
                thread.join()

            for thread in threadPoolServer2:
                thread.join()

            for thread in threadPoolClient:
                thread.join()

            print("Start time:"+str(startTime)+"   End time:"+str(endTime)+"   Diff:"+str(endTime-startTime))

#If experiment 1 called
else:
    createChunks()
    threadPoolClient = [Thread(target=sendSocket, args=(i,)) for i in range(threadNumber)]
    threadPoolServer = [Thread(target=readSocket, args=(i,)) for i in range(threadNumber)]

    for thread in threadPoolClient:
        thread.start()

    for thread in threadPoolServer:
        thread.start()

    for thread in threadPoolServer:
        thread.join()

    for thread in threadPoolClient:
        thread.join()

    print("Start time:"+str(startTime)+"   End time:"+str(endTime)+"   Diff:"+str(endTime-startTime))
    senderSocket.close()
    receiverSocket.close()
