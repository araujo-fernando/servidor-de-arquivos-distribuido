import sys
import socket
import re
import os
import math
import _thread

# https://docs.python.org/3/library/socket.html
def handle_msg(sudp, msg, PEERS, chunk_ids_list, chunk_path_list):
    data = msg[0]
    addr = msg[1]
    if int.from_bytes( data[0:2],byteorder='big') == 1: # hello
        print('[log] hello from: ', addr)
        # prepara mensagem query
        msg = (2).to_bytes(2,byteorder='big') # tipo
        msg = msg + ( int(addr[0].split('.')[0]) ).to_bytes(1,byteorder='big') # ip pt1
        msg = msg + ( int(addr[0].split('.')[1]) ).to_bytes(1,byteorder='big') # ip pt2
        msg = msg + ( int(addr[0].split('.')[2]) ).to_bytes(1,byteorder='big') # ip pt3
        msg = msg + ( int(addr[0].split('.')[3]) ).to_bytes(1,byteorder='big') # ip pt4
        msg = msg + ( addr[1] ).to_bytes(2,byteorder='big') # port
        msg = msg + ( 3 ).to_bytes(2,byteorder='big') # peer-ttl
        msg = msg + data[2:4] # quantidade de chunks
        msg = msg + data[4:] # lista de chunks
        # envia query
        for p in PEERS:
            sudp.sendto(msg, p)
            print('[log] query sent: ', p)
        # responde a consulta com seus chunks
        qc = int.from_bytes(data[2:4], byteorder='big') # quantidade
        query_list = []
        for i in range(4, 4 + qc*2, 2): # extrai
            query_list.append( int.from_bytes(data[i:i+2], byteorder='big') )
        matched_chunks = [element for element in query_list if element in chunk_ids_list] # extrai
        # prepara mensagem chunk info
        msg = (3).to_bytes(2,byteorder='big') # tipo
        msg = msg + ( len(matched_chunks) ).to_bytes(2,byteorder='big') # qc
        for id in matched_chunks:
            msg = msg + id.to_bytes(2,byteorder='big') # id
        #envia mensagem
        sudp.sendto(msg,addr)
    elif int.from_bytes( data[0:2],byteorder='big') == 2: # query
        TTL = int.from_bytes(data[8:10], byteorder='big')
        print('[log] query from: ', addr, 'with TTL: ', TTL)
        qc = int.from_bytes(data[10:12], byteorder='big') # quantidade
        query_list = []
        for i in range(12, 12 + qc*2, 2): # extrai
            query_list.append( int.from_bytes(data[i:i+2], byteorder='big') )
        matched_chunks = [element for element in query_list if element in chunk_ids_list] # extrai
        # prepara mensagem chunk info
        msg = (3).to_bytes(2,byteorder='big') # tipo
        msg = msg + ( len(matched_chunks) ).to_bytes(2,byteorder='big') # qc
        for id in matched_chunks:
            msg = msg + id.to_bytes(2,byteorder='big') # id
        # envia mensagem ao cliente
        ip = str(data[2])+'.'+str(data[3])+'.'+str(data[4])+'.'+str(data[5])
        port = int.from_bytes( data[6:8],byteorder='big')
        sudp.connect((ip,port))
        sudp.sendto(msg, (ip, port))
        # repassa mensagem aos peers conectados
        if TTL > 0:
            ttl = TTL - 1
            msg = data[0:8] + ttl.to_bytes(2,byteorder='big') + data[10:]
            for p in PEERS:
                sudp.sendto(msg, p)
                print('[log] query hop:  ', p, 'with TTL: ', TTL - 1)
    elif int.from_bytes( data[0:2],byteorder='big') == 4: # get
        print('[log] get received from: ', addr)
        qc = int.from_bytes(data[2:4], byteorder='big') # quantidade
        requested = []
        for i in range(4, 4 + qc*2, 2): # extrai
            requested.append( int.from_bytes(data[i:i+2], byteorder='big') )
        # processamento do envio
        for chunk in requested:
            # leitura do arquivo
            c_path = chunk_path_list[ chunk_ids_list.index( chunk ) ]
            file = open(c_path, "rb")
            payload = file.read()
            file.close()
            if len(payload) > 1024:
                print('[err] file too large, sending only first 1024B')
                payload = payload[0:1024]
            # construcao da mensagem
            msg = (5).to_bytes(2,byteorder='big') # tipo
            msg = msg + ( chunk ).to_bytes(2,byteorder='big') # chunk id
            msg = msg + ( len(payload) ).to_bytes(2,byteorder='big') # chunk size
            msg = msg + payload # chunk
            #envio
            sudp.sendto(msg,addr)
        print('[log] sent ',  len(requested), ' chunks to: ', addr)
    print('[log] thread exit')
    _thread.exit()

# ==============================================================================
# ===========================   MAIN   =========================================
# ==============================================================================
if  len(sys.argv) < 4:
    print('Usage: python3 peer.py <ip:port> <file.xxx> {ip_peers:port}')
    sys.exit()
# converter o endereço
SELF = sys.argv[1]
self_ip = SELF.split(':')[0]
self_port = int(SELF.split(':')[1])
# arquivo de chaves
KEYS = sys.argv[2]
k_file = open(KEYS,'r')
path = k_file.readlines()
chunk_ids_list = []
chunk_path_list = []
for i in range(len(path)):
    p = path[i];
    id = int(p[ 0 : p.index(':') ])
    chunk_ids_list.append(id)
    chunk_path_list.append(p[(p.index(':') + 2) : len(p)-1])
# peers conectados
PEERS = []
for i in range(3,len(sys.argv)):
    p = sys.argv[i]
    p_ip = p.split(':')[0]
    p_port = int(p.split(':')[1])
    PEERS.append((p_ip, p_port))
# abertura do socket
sudp = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
sudp.bind((self_ip, self_port))
sudp.settimeout(600)
# loop de escuta do peer
RUNNING = True
print('[log] socket success: ', SELF)
while RUNNING:
    msg = sudp.recvfrom(1040)
    data = msg[0]
    if int.from_bytes( data[0:2],byteorder='big') in [1, 2, 4]:
        print("[log] thread dispatch")
        _thread.start_new_thread(handle_msg,(sudp, msg, PEERS, chunk_ids_list, chunk_path_list))
    else:
        print("[log] Handshake error: unidentified message type")
print('[log] shutting down')
