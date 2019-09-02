#! /usr/bin/python

import sys, time
from socket import *
from threading import Event, Lock, Thread, Timer

DEFAULT_PORT = 10001
BUFSIZE = 1024
totalBits = 0
countBits = 0
killThread = False
mutex = Lock()


def main():
    if len(sys.argv) < 2:
        usage()
    if sys.argv[1] == '-sr':
        serverReceiver()
    elif sys.argv[1] == '-ss':
        serverSender()
    elif sys.argv[1] == '-cr':
       clientReceiver()
    elif sys.argv[1] == '-cs':
        clientSender()
    else:
        usage()


def usage():
    sys.stdout = sys.stderr
    print('Usage:    socket-throughput -sr [port]')
    print('and then: socket-throughput -cs count host_A [port]')
    print('or usage: socket-throughput -ss count [port] ')
    print('and then: scoket-throughput -cr host_A [port]')
    sys.exit(2)

def throughtputBySecond():
    global totalBits
    global countBits
    global killThread
    ticker = Event() 
    while not ticker.wait(1.0):
        mutex.acquire()
        totalBits = totalBits + countBits
        if killThread:
            ticker.clear()
            mutex.release()
            break
        print('Throughput:', round((countBits*0.001), 3), 'K/sec.')
        countBits = 0
        mutex.release()

def serverReceiver():
    global countBits
    global totaltBits
    global killThread
    if len(sys.argv) > 2:
        port = eval(sys.argv[2])
    else:
        port = DEFAULT_PORT
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    print('Server ready...')
    while 1:
        conn, (host, remoteport) = s.accept()
        thread = Thread(target=throughtputBySecond) 
        thread.start()	
        t1 = time.time()
        while 1:
            data = conn.recv(BUFSIZE)
            mutex.acquire()
            countBits = countBits + len(data)
            mutex.release()
            if not data:
                break
            del data
        t2 = time.time()
        conn.send(bytearray('OK\n', 'UTF-8'))
        conn.close()
        killThread = True
        thread.join()
        print(r'Throughput AVG:', round((totalBits*0.001) / (t2- t1), 3), 'K/sec.')
        print('Done with', host, 'port', remoteport)
        break

def serverSender():
    global countBits
    global totaltBits
    global killThread
    if len(sys.argv) < 3:
        usage()

    count = int(sys.argv[2])
    
    if len(sys.argv) > 3:
        port = eval(sys.argv[3])
    else:
        port = DEFAULT_PORT

    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)

    print('Server ready...')
    while 1:
        conn, (host, remoteport) = s.accept()
        thread = Thread(target=throughtputBySecond) 
        thread.start()	
        t1 = time.time()
        testdata = 'x' * (BUFSIZE-1) + '\n'
        i = 0
        while i < count:
            conn.send(bytearray(testdata, 'UTF-8'))
            mutex.acquire()
            countBits = countBits + len(testdata)
            mutex.release()
            i = i + 1

        t2 = time.time()
        conn.send(bytearray('OK\n', 'UTF-8'))
        conn.close()
        s.close()
        killThread = True
        thread.join()
        print(r'Throughput AVG:', round((totalBits*0.001) / (t2- t1), 3), 'K/sec.')
        print('Done with', host, 'port', remoteport)
        break


def clientReceiver():
    global countBits
    global totalBits
    global killThread
    if len(sys.argv) < 3:
       usage()
    host = sys.argv[2]
    if len(sys.argv) > 3:
        port = eval(sys.argv[3])
    else:
        port = DEFAULT_PORT
    s = socket(AF_INET, SOCK_STREAM)
    t1 = time.time()
    try:
        s.connect((host, port))
    except Exception as msg:
        print(msg)
        sys.exit()
    thread = Thread(target=throughtputBySecond) 
    thread.start()	
    while 1:
        data = s.recv(BUFSIZE)
        mutex.acquire()
        countBits = countBits + len(data)
        mutex.release()
    s.shutdown(1) # Send EOF
    t2 = time.time()


def clientSender():
    if len(sys.argv) < 4:
       usage()
    count = int(eval(sys.argv[2]))
    host = sys.argv[3]
    if len(sys.argv) > 4:
        port = eval(sys.argv[4])
    else:
        port = DEFAULT_PORT
    testdata = 'x' * (BUFSIZE-1) + '\n'
    t1 = time.time()
    s = socket(AF_INET, SOCK_STREAM)
    t2 = time.time()
    try:
        s.connect((host, port))
    except Exception as msg:
        print(msg)
        sys.exit()

    t3 = time.time()
    i = 0
    while i < count:
        i = i+1
        s.send(bytearray(testdata, 'UTF-8'))
    s.shutdown(1) # Send EOF
    t4 = time.time()
    data = s.recv(BUFSIZE)
    t5 = time.time()
    print(data)
    print('Raw timers:', t1, t2, t3, t4, t5)
    print('Intervals:', t2-t1, t3-t2, t4-t3, t5-t4)
    print('Total:', t5-t1)
    print('Throughput:', round((BUFSIZE*count*0.001) / (t4-t3), 3), 'K/sec.')


main()
