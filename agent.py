import random
from socket import *

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', 5001))
headerRecv = False
dropped = False
dropRate = 0.2
prevMsg = None
packetCount = 0
lossCount = 0

while True:
    msg, address = serverSocket.recvfrom(1024 + 50)
    toks = msg.split('\t'.encode())
    cmd = toks[0].decode()
    packetCount += 1
    if address[1] == 5000 and cmd == 'fin':
        print('get\t%s' % cmd)
        print('fwd\t%s' % cmd)
        dest = (address[0], 5002)

    elif address[1] == 5000:
        temp = [cmd, toks[1].decode()]
        if random.random() < dropRate:
            dropped = True
            lossCount += 1
            temp.extend((lossCount / packetCount, ))
            print('drop\t%s\t#%s,\tloss rate = %.4f' % tuple(temp))
            continue
        print('get\t%s\t#%s' % (temp[0], temp[1]))
        print('fwd\t%s\t#%s' % (temp[0], temp[1]))
        dest = (address[0], 5002)

    elif address[1] == 5002:
        message = msg.decode()
        try:
            message = '%s\t#%s' % tuple(message.split('\t'))
        except:
            pass
        print('get\t%s' % message)
        print('fwd\t%s' % message)
        dest = (address[0], 5000)
    serverSocket.sendto(msg, dest)

