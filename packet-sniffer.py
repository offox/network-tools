#!/usr/bin/env python

from threading import Event, Lock, Thread 
import socket
import struct
import binascii

mutex = Lock()

s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))

countBits = 0

def throughtputBySecond():
    global countBits
    ticker = Event() 
    while not ticker.wait(1.0):
        mutex.acquire()
        #if killThread:
        #    ticker.clear()
        #    mutex.release()
        #    break
        print('Throughput:', round((countBits*0.001), 3), 'K/sec.')
        countBits = 0
        mutex.release()


def main():
    global countBits
    thread = Thread(target=throughtputBySecond)
    thread.start()
    while True:
        global countBits
        packet = s.recvfrom(65535)
        # ethernet_header = packet[0][0:14]
        # eth_header = struct.unpack("!6s6s2s", ethernet_header)
        #print("Source MAC:" + str(binascii.hexlify(eth_header[0])) + " Source MAC:" + str(binascii.hexlify(eth_header[1])) + " Type:" + str(binascii.hexlify(eth_header[2])))

        ipheader = packet[0][14:38]
        ip_header = struct.unpack("!2s2s8s4s4s2s2s", ipheader)
        # print("Total length: " + str(int.from_bytes(ip_header[1], byteorder='big')) + " Source IP:" + str(socket.inet_ntoa(ip_header[3]) + " Destination IP:" + str(socket.inet_ntoa(ip_header[4]))) + " Source Port: " + str(int.from_bytes(ip_header[5], byteorder='big')) + " Destination Port: " + str(int.from_bytes(ip_header[6], byteorder='big')))

        if int.from_bytes(ip_header[5], byteorder='big') == 10004:
            countBits = countBits + int.from_bytes(ip_header[1], byteorder='big')
            #if not (count % 100000):

    #print("Source IP:" + binascii.hexlify(eth_header[0]) + "Source MAC: " +)

main()
