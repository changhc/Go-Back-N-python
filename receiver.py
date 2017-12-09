import time
import pickle
import argparse
from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('output_name')
args = parser.parse_args()

with open('receiver.conf') as f:
    addr = (f.readline().strip().split('=')[1],
            int(f.readline().strip().split('=')[1]))
    BUFFER_SIZE = int(f.readline().strip().split('=')[1])
pointer = -1
receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind(addr)
outputFile = None

collected = [None] * BUFFER_SIZE
count = 0
flushed = False
while True: 
    try:
        pkt, agentAddr = receiverSocket.recvfrom(1024 + 100)
        pkt = pickle.loads(pkt)
        cmd = pkt[2]
        if not outputFile:
            ext = cmd[3].split('.')
            if len(ext) == 1:
                ext = ''
            else:
                ext = '.' + ext[-1]
            outputFile = open('%s%s' % (args.output_name, ext), 'wb')
        if cmd[0] == 'fin':
            print('recv\tfin')
            print('send\tfinack')
            msg = [addr, pkt[0], ['finack']]
            receiverSocket.sendto(pickle.dumps(msg), agentAddr)
            break
        idx = int(cmd[1])
        data = cmd[2]
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
        message = [addr, pkt[0], ['ack', pointer]]
        print('send\tack\t#%d' % pointer)
        if count == BUFFER_SIZE and flushed:
            flushed = False
            print('flush')
            count = 0
        receiverSocket.sendto(pickle.dumps(message), agentAddr)
    except timeout:
        print('REQUEST TIMED OUT')

for item in collected:
    if item is not None:
        outputFile.write(item)
print('flush')
outputFile.close()
