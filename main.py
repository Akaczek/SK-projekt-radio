import socket
import time

import pyaudio

HOST = "192.168.100.208"
PORT = 4444


def polacz():
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_out.connect((HOST, PORT))
    sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_in.connect((HOST, PORT))

    return sock_out, sock_in


def zakoncz(sock1, sock2):
    sock1.shutdown(socket.SHUT_WR)
    sock1.close()
    sock2.shutdown(socket.SHUT_WR)
    sock2.close()

def receiveAudio(nazwa_pliku, sock):
    sock.send(bytes(nazwa_pliku, "utf-8"))
    sock.settimeout(1)
    while True:
        try:
            data = sock.recv(4096)
            stream.write(data)
        except socket.timeout:
            break
    sock.settimeout(None)

def sendFile(nazwa_pliku, sock):
    print("Wysyłanie...")
    sock.send(bytes(nazwa_pliku, "utf-8"))

    wf = open(nazwa_pliku + ".wav", 'rb')
    audio = wf.read()
    n = 12000
    data = [audio[i : i+n] for i in range(0, len(audio), n)]

    for i in data:
        sock.send(i)
    print("Plik wysłany")
    wf.close()


p = pyaudio.PyAudio()
CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

if __name__ == "__main__":
    sock_out, sock_in = polacz()
    sendFile("145276", sock_out)
    time.sleep(1)
    receiveAudio("145276",sock_in)
    zakoncz(sock_out, sock_in)


stream.stop_stream()
stream.close()
p.terminate()
