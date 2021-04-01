
import sys
import socket
import re
import os
import math
import time

# https://docs.python.org/3/library/socket.html
if  len(sys.argv) != 3:
    print('Usage: python3 cliente.py <peer_ip:port> <chunks>')
    sys.exit()
# converter o endereço
PEER = sys.argv[1]
peer_ip = PEER.split(':')[0]
peer_port = int(PEER.split(':')[1])
# converter o argumento para lista numérica
CHUNKS = sys.argv[2]
chunk_list = (CHUNKS.replace(',',' ')).split()
chunk_ids = [int(num) for num in chunk_list]
chunk_count = len(chunk_ids)
# abertura do socket
sudp = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
print('[log] client socket success: ',sudp.getsockname())
# envia HELLO
msg = (1).to_bytes(2,byteorder='big')
msg = msg + ( chunk_count ).to_bytes(2,byteorder='big')
for id in chunk_ids:
    msg = msg + ( id ).to_bytes(2,byteorder='big')
sudp.sendto(msg,(peer_ip,peer_port))
print('[log] hello success: ', (peer_ip,peer_port))
# aguardar respostas CHUNK Info
chunk_info = []
sudp.settimeout(10)
print('[log] chunk info: begin')
repeat = True
while repeat:
    try:
        msg = sudp.recvfrom(1040)# tupla (bytes, addr)
        data = msg[0]
        addr = msg[1]
        if int.from_bytes( data[0:2],byteorder='big') == 3:
            chunk_info.append(msg) # tupla (chunk info, addr)
            print('[log] received chunk info:', addr)
        else:
            print("[log] Handshake error: chunk info")
    except socket.timeout:
        repeat = False
print('[log] chunk info: end')
# solicitar envio
pending_requests = chunk_ids
for info in chunk_info:
    data  = info[0]
    paddr = info[1]
    qc = int.from_bytes(data[2:4], byteorder='big') # quantidade
    query_list = []
    for i in range(4, 4 + qc*2, 2): # extrai
        query_list.append( int.from_bytes(data[i:i+2], byteorder='big') )
    matched_chunks = [element for element in query_list if element in pending_requests] # extrai
    # prepara mensagem get
    if len(matched_chunks) > 0:
        msg = (4).to_bytes(2,byteorder='big') # tipo
        msg = msg + ( len(matched_chunks) ).to_bytes(2,byteorder='big') # qc
        for id in matched_chunks:
            msg = msg + id.to_bytes(2,byteorder='big') # id
        #envia mensagem
        sudp.sendto(msg,paddr)
        # remove chunks solicitados da lista
        pending_requests = [element for element in pending_requests if element not in matched_chunks]
    if len(pending_requests)==0:
        break
# chunks solicitados nao encontrados
if len(pending_requests) > 0:
    print('[wrn] incomplete transfer will begin')
    print('[wrn] program termination is advised')
    for i in range(10):
        print('[wrn] incomplete transfer in: ',str(10-i),' seconds')
        time.sleep(1)
# receber transferencia
self_ip = sudp.getsockname()[0]
logPath = os.path.join(os.getcwd(), 'output-' + self_ip + '.log')
logFile = open(logPath,'w')
repeat = True
while repeat:
    try:
        msg = sudp.recvfrom(1040)# tupla (bytes, addr)
        data = msg[0]
        addr = msg[1]
        if int.from_bytes( data[0:2],byteorder='big') == 5: # response
            id = int.from_bytes( data[2:4],byteorder='big')
            savePath = os.path.join(os.getcwd(),'received_files')
            try:
                os.mkdir(savePath)
            except OSError as error:
                pass
            savePath = os.path.join(savePath,'littleBunny_' + str(id) + '.m4s')
            file = open(savePath,'wb')
            file.write(data[4:])
            file.close()

            print(addr[0] + ':' + str(addr[1]) + ' - ' + str(id) ,file = logFile)
            print('[log] received chunk: ',str(id) ,' from: ', addr)
        else:
            print("[log] Handshake error: response")
    except socket.timeout:
        repeat = False
for p in pending_requests:
    print('0.0.0.0:0 - ' + str(p) ,file = logFile)
logFile.close()
print('[log] transfer terminated')
