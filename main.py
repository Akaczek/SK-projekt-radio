import socket
import time
import threading
import pyaudio
import pygame
import os

HOST = "192.168.100.213"
PORT = 8000

X = 500
Y = 250
green = (0,255,0)
red = (255,0,0)
black = (0, 0, 0)
white = (255,255,255)
color_light = (170,170,170)
color_dark = (100,100,100)

def whatGoodToSend():
    do_wyslania = []
    files = os.listdir("./")
    for file in files:
        if file[-3] == 'w':
            do_wyslania.append(file[:-4])
    return do_wyslania



def polacz():
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_out.connect((HOST, PORT))
    time.sleep(0.1)
    sock_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_in.connect((HOST, PORT))
    time.sleep(0.1)
    sock_kom = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_kom.connect((HOST, PORT))

    return sock_out, sock_in, sock_kom


def zakoncz(sock):
    sock.shutdown(socket.SHUT_WR)
    sock.close()

def receiveList(sock):
    lista = ""
    while True:
        try:
            sock.settimeout(2)
            lista += sock.recv(64).decode("utf-8")
        except socket.timeout:
            break
    return lista.split("|")[:-1]

def receiveAudio(sock):
    while True:
        try:
            sock.settimeout(2)
            data = sock.recv(8192)
            stream.write(data)
            sock.settimeout(None)
        except (socket.timeout, OSError):
            break


def sendFile(nazwa_pliku, sock):
    print("Wysyłanie...")
    sock.send(bytes(nazwa_pliku, "utf-8"))

    wf = open(nazwa_pliku + ".wav", 'rb')
    audio = wf.read()
    n = 12000
    data = [audio[i : i+n] for i in range(0, len(audio), n)]

    for i in data:
        sock.send(i)
    time.sleep(3)
    sock.send(bytes("koniec", "utf-8"))
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

okno = "start"
running = True

if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode([X,Y])
    pygame.display.set_caption('Radio')
    connected = True

    font = pygame.font.SysFont('arial', 16)

    przycisk_startu = pygame.Rect(100, 100, 100, 100)
    przycisk_startu.center = (X//2, Y//2)

    przycisk_stopu = pygame.Rect(400,20,80,80)
    stop = pygame.Rect(0,0,50,50)
    stop.center = przycisk_stopu.center

    przycisk_dodaj = pygame.Rect(400, 150, 80, 80)
    pionowo = pygame.Rect(0, 0, 20, 60)
    poziomo = pygame.Rect(0, 0, 60, 20)
    pionowo.center = przycisk_dodaj.center
    poziomo.center = przycisk_dodaj.center

    przycisk_gora = pygame.Rect(350, Y//2 - 80, 40, 40)

    przycisk_dol = pygame.Rect(350, Y//2 + 40, 40, 40)

    przycisk_wyslij = pygame.Rect(345, 100, 50, 50)

    przycisk_cofnij = pygame.Rect(410, 100, 50, 50)


    ktore_dodaj = 0
    ktore_kolejka = 0

    flaga = True

    screen.fill((255, 255, 255))
    # główna pętla
    while running:
        mouse = pygame.mouse.get_pos()

        #okno startowe
        if okno == "start":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    connected = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if X / 2 - 50 <= mouse[0] <= X / 2 + 50 and Y / 2 - 50 <= mouse[1] <= Y / 2 + 50:
                        try:
                            sock_out, sock_in, sock_kom = polacz()
                            t1 = threading.Thread(target=receiveAudio, args=(sock_in,))
                            t1.start()
                        except (ConnectionRefusedError, TimeoutError):
                            connected = False
                        if connected:
                            sock_kom.send(bytes("lista", "utf-8"))
                            kolejka = receiveList(sock_kom)
                        else:
                            text = font.render('Nie można uzyskać połączenia', True, (0, 0, 0))
                            textRect = text.get_rect()
                            textRect.center = (X // 2, Y // 2)
                        okno = "radio"


                if X / 2 - 50 <= mouse[0] <= X / 2 + 50 and Y / 2 - 50 <= mouse[1] <= Y / 2 + 50:
                    pygame.draw.rect(screen, color_light, przycisk_startu,  border_radius=3)

                else:
                    pygame.draw.rect(screen, color_dark, przycisk_startu, border_radius=3)
                pygame.draw.polygon(screen, green, ((X//2-30, Y//2 + 40), (X//2 - 30, Y//2 - 40), (X//2 + 30, Y//2)))
            pygame.display.update()

        #jest okno radia
        if okno == "radio":
            screen.fill((255, 255, 255))
            # jeśli połączony
            if connected:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sock_kom.send(bytes("close", "utf-8"))
                        zakoncz(sock_out)
                        running = False;
                        time.sleep(0.5)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if 400 <= mouse[0] <= 480 and 20 <= mouse[1] <= 100:
                            sock_kom.send(bytes("close", "utf-8"))
                            zakoncz(sock_out)
                            t1.join(2)
                            zakoncz(sock_in)
                            zakoncz(sock_kom)
                            okno = "start"
                        if 400 <= mouse[0] <= 480 and 150 <= mouse[1] <= 230:
                            lista_do_wyslania = []
                            lista_do_wyslania = whatGoodToSend()
                            sock_kom.send(bytes("lista", "utf-8"))
                            kolejka = receiveList(sock_kom)
                            print(kolejka)
                            lista_do_wyslania = list(set(lista_do_wyslania).difference(kolejka))
                            print(lista_do_wyslania)
                            okno = "dodaj"

                        if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                            sock_kom.send(bytes("zmiana", "utf-8"))
                            time.sleep(1)
                            sock_kom.send(bytes(str(ktore_kolejka), "utf-8"))
                        if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                            if ktore_kolejka > 0:
                                ktore_kolejka -= 1
                        if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                            if ktore_kolejka < len(kolejka) - 1:
                                ktore_kolejka += 1

                if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                    pygame.draw.rect(screen, color_light, przycisk_wyslij, border_radius=3)
                else:
                    pygame.draw.rect(screen, color_dark, przycisk_wyslij, border_radius=3)

                if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                    pygame.draw.rect(screen, color_light, przycisk_gora, border_radius=3)
                else:
                    pygame.draw.rect(screen, color_dark, przycisk_gora, border_radius=3)

                if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                    pygame.draw.rect(screen, color_light, przycisk_dol, border_radius=3)
                else:
                    pygame.draw.rect(screen, color_dark, przycisk_dol, border_radius=3)

                #przycisk stopu
                if 400 <= mouse[0] <= 480 and 20 <= mouse[1] <= 100:
                    pygame.draw.rect(screen, color_dark, przycisk_stopu, border_radius=3)
                else:
                    pygame.draw.rect(screen, color_light, przycisk_stopu, border_radius=3)
                pygame.draw.rect(screen, red, stop)

                #przycisk dodaj
                if 400 <= mouse[0] <= 480 and 150 <= mouse[1] <= 230:
                    pygame.draw.rect(screen, color_dark, przycisk_dodaj, border_radius=3)
                else:
                    pygame.draw.rect(screen, color_light, przycisk_dodaj, border_radius=3)
                pygame.draw.rect(screen, black, pionowo)
                pygame.draw.rect(screen, black, poziomo)

                #wyswietlenie kolejki
                for i in range(len(kolejka)):
                    text = font.render(kolejka[i], True, black)
                    textRect = text.get_rect()
                    textRect.center = (100, (Y // 2 + i * 30) - (ktore_kolejka * 30))
                    screen.blit(text, textRect)

                #przejscie do okna start
                if okno == "start":
                    screen.fill((255, 255, 255))
                    pygame.display.update()
                #przejscie do okna dodaj
                if okno == "dodaj":
                    screen.fill((255, 255, 255))
                    pygame.display.update()


            # jeśli nie połączony
            else:
                screen.blit(text, textRect)
                for event in pygame.event.get():
                    pygame.display.update()
                    if event.type == pygame.QUIT:
                        running = False;
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        print("click", mouse[0], mouse[1])
            pygame.display.update()


        if okno == "dodaj":
            screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sock_kom.send(bytes("close", "utf-8"))
                    zakoncz(sock_out)
                    running = False;
                    time.sleep(0.5)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 410 <= mouse[0] <= 460 and 100 <= mouse[1] <= 150:
                        okno = "radio"
                    if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                        if ktore_dodaj > 0:
                            ktore_dodaj -= 1
                    if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                        if ktore_dodaj < len(lista_do_wyslania) - 1:
                            ktore_dodaj += 1
                    if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                        if lista_do_wyslania:
                            sendFile(lista_do_wyslania[ktore_dodaj], sock_out)
                            okno = "radio"


            if 410 <= mouse[0] <= 460 and 100 <= mouse[1] <= 150:
                pygame.draw.rect(screen, color_light, przycisk_cofnij, border_radius=3)
            else:
                pygame.draw.rect(screen, color_dark, przycisk_cofnij, border_radius=3)

            if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                pygame.draw.rect(screen, color_light, przycisk_gora, border_radius=3)
            else:
                pygame.draw.rect(screen, color_dark, przycisk_gora, border_radius=3)

            if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                pygame.draw.rect(screen, color_light, przycisk_dol, border_radius=3)
            else:
                pygame.draw.rect(screen, color_dark, przycisk_dol, border_radius=3)

            if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                pygame.draw.rect(screen, color_light, przycisk_wyslij, border_radius=3)
            else:
                pygame.draw.rect(screen, color_dark, przycisk_wyslij, border_radius=3)

            for i in range(len(lista_do_wyslania)):
                text = font.render(lista_do_wyslania[i], True, black)
                textRect = text.get_rect()
                textRect.center = (100 , (Y//2 + i * 30) - (ktore_dodaj * 30))
                screen.blit(text, textRect)

            if okno == "radio":
                ktore_dodaj = 0
                flaga = True
                screen.fill((255, 255, 255))
                sock_kom.send(bytes("lista", "utf-8"))
                kolejka = receiveList(sock_kom)
                pygame.display.update()

            pygame.display.update()

    # zamknięcie wątków i połączeń
    if connected:
        t1.join(2)
        zakoncz(sock_in)
        zakoncz(sock_kom)
        time.sleep(1)
    pygame.quit()
    quit()



