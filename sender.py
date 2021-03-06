import time
import math
import pickle
import argparse
from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('input_name')
args = parser.parse_args()

with open('sender.conf') as f:
    addr = (f.readline().strip().split('=')[1],
            int(f.readline().strip().split('=')[1]))
    agentAddr = (f.readline().strip().split('=')[1],
              int(f.readline().strip().split('=')[1]))
    targetAddr = (f.readline().strip().split('=')[1],
              int(f.readline().strip().split('=')[1])) 
    THRESHOLD = int(f.readline().strip().split('=')[1])
TIMEOUT = 1
pointer = 0
maxIdx = -1
winSize = 1
packetSize = 1024
senderSocket = socket(AF_INET, SOCK_DGRAM)
senderSocket.settimeout(0.001) # small unit
senderSocket.bind(addr)
startTime = time.time()

with open(args.input_name, 'rb') as f:
    data = []
    while True:
        temp = f.read(packetSize)
        if not temp:
            break
        data.extend((temp, ))

while pointer < len(data):
    sentCount = 0
    for i in range(winSize):
        if pointer + i >= len(data):
            break
        message = data[pointer + i]
        if pointer + i <= maxIdx:
            print('resnd\tdata\t#%d,\twinSize = %d' % (pointer + i, winSize))
        else:
            print('send\tdata\t#%d,\twinSize = %d' % (pointer + i, winSize))
        # msg = [addr, receiver, body]
        temp = [addr, targetAddr, ['data', pointer + i, message, args.input_name]]
        senderSocket.sendto(pickle.dumps(temp), agentAddr)
        sentCount += 1
        if i == 0:
            startTime = time.time()
    maxIdx = pointer + sentCount - 1

    acked = 0
    while True:
        try:
            res, server = senderSocket.recvfrom(packetSize)
            res = pickle.loads(res)
            idx = res[2][1]
            print('recv\t%s\t#%d' % (res[2][0], idx))
            if pointer == idx:
                startTime = time.time()
                pointer += 1
                acked += 1
        except timeout:
            if time.time() - startTime > TIMEOUT and acked != sentCount:
                THRESHOLD = max(math.floor(winSize / 2), 1)
                winSize = 1
                print('time\tout,\t \tthreshold = %d' % THRESHOLD)
                break
            elif time.time() - startTime > TIMEOUT: # all acked
                if acked == winSize and winSize < THRESHOLD:
                    winSize *= 2
                elif acked == winSize:
                    winSize += 1
                break

while True:
    msg = [addr, targetAddr, ['fin']]
    senderSocket.sendto(pickle.dumps(msg), agentAddr)
    print('send\tfin')
    try:
        res, server = senderSocket.recvfrom(packetSize)
        print('recv\t%s' % pickle.loads(res)[2][0])
        break
    except timeout:
        print('time\tout')
senderSocket.close()
