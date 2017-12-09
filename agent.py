import random
import pickle
from socket import *

with open('agent.conf') as f:
    addr = (f.readline().strip().split('=')[1],
            int(f.readline().strip().split('=')[1]))
    dropRate = float(f.readline().strip().split('=')[1])
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(addr)
packetCount = 0
lossCount = 0

while True:
    msg, address = serverSocket.recvfrom(1024 + 100)
    toks = pickle.loads(msg)
    dest = toks[1]
    cmd = toks[2]

    if cmd[0] == 'fin' or cmd[0] == 'finack':
        print('get\t%s' % cmd[0])
        print('fwd\t%s' % cmd[0])
    else:
        temp = [cmd[0], cmd[1]]
        print('get\t%s\t#%s' % (temp[0], temp[1]))
        if cmd[0] == 'data':
            packetCount += 1
            if random.random() < dropRate:
                dropped = True
                lossCount += 1
                temp.extend((lossCount / packetCount, ))
                print('drop\t%s\t#%s,\tloss rate = %.4f' % tuple(temp))
                continue
        print('fwd\t%s\t#%s' % (temp[0], temp[1]))

    serverSocket.sendto(msg, dest)

