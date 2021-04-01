@ECHO OFF
cd PATH/TO/CODE
start cmd /k python peer.py 127.0.0.1:60001 keys1.txt 127.0.0.3:60003 127.0.0.2:60002
start cmd /k python peer.py 127.0.0.2:60002 keys2.txt 127.0.0.1:60001 127.0.0.5:60005
start cmd /k python peer.py 127.0.0.3:60003 keys3.txt 127.0.0.1:60001 127.0.0.5:60005
start cmd /k python peer.py 127.0.0.4:60004 keys4.txt 127.0.0.5:60005
start cmd /k python peer.py 127.0.0.5:60005 keys5.txt 127.0.0.2:60002 127.0.0.3:60003 127.0.0.4:60004
timeout /t 10 /nobreak > NUL
start cmd /k python cliente.py 127.0.0.1:60001 1,3,2,4,5
timeout /t 75 /nobreak > NUL
start cmd /k python cliente.py 127.0.0.1:60001 1,3,2,5,4,6,9
