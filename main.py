import socket
import time

HOST = "192.168.100.208"
PORT_out = 4444
PORT_in = 5555

wf = open("nowykolor.wav", 'rb')
audio = wf.read()
out = open("out.wav", mode = 'w+b')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT_out))
    s.send(bytes("nowykolor", "utf-8"))

    n = 12000
    data = [audio[i : i+n] for i in range(0, len(audio), n)]
    print(len(data[0]))
    print(len(data))

    for i in data:
        s.sendall(i)
        # out.write(s.recv(1024))


    s.shutdown(socket.SHUT_WR)
    s.close()

wf.close()
out.close()
