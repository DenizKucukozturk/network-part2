import socket
import sys
from threading import Thread
import time

#Assign port numbers
receivePorts=[50,70]
sendPorts=[60,80]
sendAddress1="10.10.5.2"
sendAddress2="10.10.2.2"

threadCount=2
receiveSocket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiveSocket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

receive_address1 = ('', receivePorts[0])
receiveSocket1.bind(receive_address1)

receive_address2 = ('', receivePorts[1])
receiveSocket2.bind(receive_address2)


#Assign clientSockets
sendSocket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sendSocket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def ReadandSend1():
    send_address = (sendAddress1, sendPorts[0])
    while(True):
        data, address = receiveSocket1.recvfrom(920)
        sendSocket1.sendto(data,send_address)

def ReadandSend2():
    send_address = (sendAddress2, sendPorts[1])
    while(True):
        data, address = receiveSocket2.recvfrom(920)
        sendSocket2.sendto(data,send_address)

try:
    thread1=Thread(target=ReadandSend1)
    thread2=Thread(target=ReadandSend2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

except:
    print("THREADING ERROR")
