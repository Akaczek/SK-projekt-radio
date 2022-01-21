import socket
import pyaudio

HOST = "192.168.100.208"
PORT = 4444


out = open("out.wav", mode = 'w+b')


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


def sendFile(nazwa_pliku, sock):
        sock.send(bytes(nazwa_pliku, "utf-8"))

        wf = open(nazwa_pliku + ".wav", 'rb')
        audio = wf.read()
        n = 12000
        data = [audio[i : i+n] for i in range(0, len(audio), n)]

        for i in data:
            sock.sendall(i)
            # out.write(s.recv(1024))
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
    # sock_out, sock_in = polacz()
    # sendFile("nowykolor", sock_out)
    # zakoncz(sock_out, sock_in)


    wf = open("nowykolor" + ".wav", 'rb')
    audio = wf.read()
    n = 12000
    data = [audio[i: i + n] for i in range(0, len(audio), n)]

    for i in data:
        stream.write(i)

stream.stop_stream()
stream.close()
p.terminate()
out.close()
