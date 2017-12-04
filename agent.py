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
    msg, address = serverSocket.recvfrom(1024)
    message = msg.decode()
    packetCount += 1
    if address[1] == 5000 and message == 'fin':
        print('get\t%s' % message)
        print('fwd\t%s' % message)
        dest = (address[0], 5002)
    elif address[1] == 5000 and not headerRecv: 
        headerRecv = True
        if random.random() < dropRate:
            dropped = True
            lossCount += 1
            temp = message.split('\t')[0:2]
            temp.extend((lossCount / packetCount, ))
            print('drop\t%s\t%s,\tloss rate = %.4f' % tuple(temp))
            continue
        prevMsg = tuple(message.split('\t')[0:2])
        dest = (address[0], 5002)
    elif address[1] == 5000 and headerRecv:
        headerRecv = False
        if dropped:
            dropped = False
            continue
        print('get\t%s\t#%s' % prevMsg)
        print('fwd\t%s\t#%s' % prevMsg)
        dest = (address[0], 5002)
    elif address[1] == 5002:
        try:
            message = '%s\t#%s' % tuple(message.split('\t'))
        except:
            pass
        print('get\t%s' % message)
        print('fwd\t%s' % message)
        dest = (address[0], 5000)
    serverSocket.sendto(msg, dest)
