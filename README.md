*Formato de uso:*

python3 cliente.py <peer_ip:port> <chunks>

python3 peer.py <ip:port> <file.xxx> {ip_peers:port}

*Exemplo:* Rede com cinco peers

1 - Inicie os peers
python peer.py 127.0.0.1:60001 keys1.txt 127.0.0.3:60003 127.0.0.2:60002

python peer.py 127.0.0.2:60002 keys2.txt 127.0.0.1:60001 127.0.0.5:60005

python peer.py 127.0.0.3:60003 keys3.txt 127.0.0.1:60001 127.0.0.5:60005

python peer.py 127.0.0.4:60004 keys4.txt 127.0.0.5:60005

python peer.py 127.0.0.5:60005 keys5.txt 127.0.0.2:60002 127.0.0.3:60003 127.0.0.4:60004


2 -  Os clientes podem se conectar à rede

python cliente.py 127.0.0.1:60001 1,3,2,4,5

python cliente.py 127.0.0.1:60001 1,3,2,5,4,6,9


*Formato do conteúdo do arquivo de chaves:*

2: path/filename_2.m4s

5: path/filename_5.m4s

3: path/filename_3.m4s
