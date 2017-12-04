import time
import math
import argparse
from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('input_name')
args = parser.parse_args()

THRESHOLD = 16
TIMEOUT = 1
pointer = 0
winSize = 1
packetSize = 1024
senderSocket = socket(AF_INET, SOCK_DGRAM)
senderSocket.settimeout(1)
senderSocket.bind(('', 5000))
agentAddr = ("127.0.0.1", 5001)

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
        print('send\tdata\t#%d,\twinSize = %d' % (pointer + i, winSize))
        senderSocket.sendto(('data\t%d\t' % (pointer + i)).encode(), agentAddr)
        senderSocket.sendto(message, agentAddr)
        sentCount += 1
    try:
#        start = time.time()
        acked = 0
        for i in range(sentCount):
            res, server = senderSocket.recvfrom(packetSize)
            res = res.decode().split('\t')
            idx = int(res[1])
            print('recv\t%s\t#%d' % (res[0], idx))
            if pointer == idx:
                pointer += 1
                acked += 1
        if acked == winSize and winSize < THRESHOLD:
            winSize *= 2
        elif acked == winSize:
            winSize += 1
#                start = time.time()
#            if time.time() - start > TIMEOUT:
#                raise timeout
    except timeout:
        THRESHOLD = max(math.floor(winSize / 2), 1)
        winSize = 1
        print('time\tout,\t \tthreshold = %d' % THRESHOLD)

while True:
    senderSocket.sendto('fin'.encode(), agentAddr)
    print('send\tfin')
    try:
        res, server = senderSocket.recvfrom(packetSize)
        print('recv\t%s' % res.decode())
        break
    except timeout:
        print('time\tout')

