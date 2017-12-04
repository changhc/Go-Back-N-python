import time
from socket import *

BUFFER_SIZE = 5
pointer = -1
receiverSocket = socket(AF_INET, SOCK_DGRAM)
#senderSocket.settimeout(1)
receiverSocket.bind(('', 5002))
agentAddr = ('127.0.0.1', 5001)
outputFile = open('output', 'wb')

collected = [None] * BUFFER_SIZE
count = 0
flushed = False
while True: 
    try:
        cmd, _ = receiverSocket.recvfrom(1024)
        cmd = cmd.decode().split('\t')
        if cmd[0] == 'fin':
            print('recv\tfin')
            print('send\tfinack')
            receiverSocket.sendto('finack'.encode(), agentAddr)
            break
        idx = int(cmd[1])
        data, _ = receiverSocket.recvfrom(1024)
        if (pointer + 1) % BUFFER_SIZE == 0 and count == BUFFER_SIZE:
            # buffer overflow
            flushed = True
            print('drop\tdata\t#%d' % idx)
            for i in range(BUFFER_SIZE):
                outputFile.write(collected[i])
                collected[i] = None

        elif idx == (pointer + 1):
            pointer += 1
            count += 1
            collected[pointer % BUFFER_SIZE] = data
            print('recv\tdata\t#%d' % pointer)
        message = 'ack\t%d' % pointer
        print('send\tack\t#%d' % pointer)
        if count == BUFFER_SIZE and flushed:
            flushed = False
            print('flush')
            count = 0
        receiverSocket.sendto(message.encode(), agentAddr)
    except timeout:
        print('REQUEST TIMED OUT')

for item in collected:
    if item is not None:
        outputFile.write(item)
print('flush')
outputFile.close()
