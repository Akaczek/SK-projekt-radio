import socket
import time
import threading
import pyaudio
import pygame
import os

X = 500
Y = 250
green = (0,255,0)
red = (255,0,0)
black = (0, 0, 0)
white = (255,255,255)
navy_blue = (3,14,79)
navy_blue_light = (6, 26, 143)
yellow = (244,158,28)

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
    time.sleep(1)
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

HOST = "192.168.100.213"
PORT = "8001"

if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode([X,Y])
    pygame.display.set_caption('Radio')
    connected = True

    font = pygame.font.SysFont('arial', 16)
    fontBig = pygame.font.SysFont('arial', 32)

    przycisk_startu = pygame.Rect(100, 100, 100, 100)
    przycisk_startu.center = (X//2, Y//2 + 50)

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

    przycisk_usun = pygame.Rect(300, 10, 50, 20)

    podswietlenie = pygame.Rect(40, 110, 250, 30)

    input_host = pygame.Rect(0, 0, 140, 32)
    input_host.center = (X//2, 30)

    input_port = pygame.Rect(0, 0, 70, 32)
    input_port.center = (X//2, 72)

    ktore_dodaj = 0
    ktore_kolejka = 0

    flaga = True
    active_port = False
    active_host = False

    screen.fill(yellow)
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
                    if input_port.collidepoint(event.pos):
                        active_port = True
                    else:
                        active_port = False

                    if input_host.collidepoint(event.pos):
                        active_host = True
                    else:
                        active_host = False

                    if X / 2 - 50 <= mouse[0] <= X / 2 + 50 and Y / 2 <= mouse[1] <= Y / 2 + 100:
                        try:
                            if HOST == "":
                                HOST = "192.168.100.213"
                            if PORT == "":
                                PORT = 8001
                            else:
                                PORT = int(PORT)
                            sock_out, sock_in, sock_kom = polacz()
                            t1 = threading.Thread(target=receiveAudio, args=(sock_in,))
                            t1.start()
                        except Exception as e:
                            connected = False
                        if connected:
                            sock_kom.send(bytes("lista", "utf-8"))
                            kolejka = receiveList(sock_kom)
                        else:
                            text = font.render('Nie można uzyskać połączenia', True, (0, 0, 0))
                            textRect = text.get_rect()
                            textRect.center = (X // 2, Y // 2)
                        okno = "radio"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if active_host:
                            HOST = HOST[:-1]
                        if active_port:
                            PORT = PORT[:-1]
                    else:
                        if active_host:
                            HOST += event.unicode
                        if active_port:
                            PORT += event.unicode

                if okno != "radio":
                    pygame.draw.rect(screen, white, input_host)
                    text_surface = font.render(HOST, True, black)
                    screen.blit(text_surface, (input_host.x + 5, input_host.y + 5))

                    pygame.draw.rect(screen, white, input_port)
                    text_surface = font.render(PORT, True, black)
                    screen.blit(text_surface, (input_port.x + 5, input_port.y + 5))

                if X / 2 - 50 <= mouse[0] <= X / 2 + 50 and Y / 2 <= mouse[1] <= Y / 2 + 100:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_startu,  border_radius=3)

                else:
                    pygame.draw.rect(screen, navy_blue, przycisk_startu, border_radius=3)
                pygame.draw.polygon(screen, green, ((X//2-30, Y//2 + 90), (X//2 - 30, Y//2 + 10), (X//2 + 30, Y//2 + 50)))
            pygame.display.update()

        #jest okno radia
        if okno == "radio":
            screen.fill(yellow)

            # jeśli połączony
            if connected:
                pygame.draw.rect(screen, white, podswietlenie)
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
                            lista_do_wyslania = list(set(lista_do_wyslania).difference(kolejka))
                            okno = "dodaj"

                        if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                            sock_kom.send(bytes("zmiana", "utf-8"))
                            time.sleep(1)
                            sock_kom.send(bytes(str(ktore_kolejka), "utf-8"))
                        if 300 <= mouse[0] <= 350 and 10 <= mouse[1] <= 30:
                            sock_kom.send(bytes("usun", "utf-8"))
                            time.sleep(1)
                            sock_kom.send(bytes(str(ktore_kolejka), "utf-8"))
                            time.sleep(1)
                            sock_kom.send(bytes("lista", "utf-8"))
                            kolejka = receiveList(sock_kom)
                        if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                            if ktore_kolejka > 0:
                                ktore_kolejka -= 1
                        if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                            if ktore_kolejka < len(kolejka) - 1:
                                ktore_kolejka += 1

                #przycisk_wlacz
                if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_wyslij, border_radius=3)
                else:
                    pygame.draw.rect(screen, navy_blue, przycisk_wyslij, border_radius=3)
                pygame.draw.polygon(screen, green, ((przycisk_wyslij.centerx - 15, przycisk_wyslij.centery - 15),
                                                   (przycisk_wyslij.centerx - 15, przycisk_wyslij.centery + 15),
                                                   (przycisk_wyslij.centerx + 15, przycisk_wyslij.centery)))

                #przycisk_w_gore
                if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_gora, border_radius=3)
                else:
                    pygame.draw.rect(screen, navy_blue, przycisk_gora, border_radius=3)
                pygame.draw.polygon(screen, white, ((przycisk_gora.centerx - 10, przycisk_gora.centery + 10),
                                                        (przycisk_gora.centerx + 10, przycisk_gora.centery + 10),
                                                        (przycisk_gora.centerx, przycisk_gora.centery - 10)))

                #przycisk_w_dol
                if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_dol, border_radius=3)
                else:
                    pygame.draw.rect(screen, navy_blue, przycisk_dol, border_radius=3)
                pygame.draw.polygon(screen, white, ((przycisk_dol.centerx - 10, przycisk_dol.centery - 10),
                                                    (przycisk_dol.centerx + 10, przycisk_dol.centery - 10),
                                                    (przycisk_dol.centerx, przycisk_dol.centery + 10)))

                #przycisk_usun
                if 300 <= mouse[0] <= 350 and 10 <= mouse[1] <= 30:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_usun, border_radius=3)
                else:
                    pygame.draw.rect(screen, navy_blue, przycisk_usun, border_radius=3)
                text = font.render("Usuń", True, white)
                textRect = text.get_rect()
                textRect.center = przycisk_usun.center
                screen.blit(text, textRect)

                #przycisk stopu
                if 400 <= mouse[0] <= 480 and 20 <= mouse[1] <= 100:
                    pygame.draw.rect(screen, navy_blue, przycisk_stopu, border_radius=3)
                else:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_stopu, border_radius=3)
                pygame.draw.rect(screen, red, stop)

                #przycisk dodaj
                if 400 <= mouse[0] <= 480 and 150 <= mouse[1] <= 230:
                    pygame.draw.rect(screen, navy_blue, przycisk_dodaj, border_radius=3)
                else:
                    pygame.draw.rect(screen, navy_blue_light, przycisk_dodaj, border_radius=3)
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
                    screen.fill(yellow)
                    pygame.display.update()
                #przejscie do okna dodaj
                if okno == "dodaj":
                    screen.fill(yellow)
                    pygame.display.update()


            # jeśli nie połączony
            else:
                screen.blit(text, textRect)
                for event in pygame.event.get():
                    pygame.display.update()
                    if event.type == pygame.QUIT:
                        running = False;
            pygame.display.update()


        if okno == "dodaj":
            screen.fill(yellow)
            pygame.draw.rect(screen, white, podswietlenie)
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
                            text = fontBig.render("Trwa wysyłanie..", True, black)
                            textRect = text.get_rect()
                            textRect.center = (250, 30)
                            screen.fill(yellow)
                            screen.blit(text, textRect)
                            pygame.display.update()
                            sendFile(lista_do_wyslania[ktore_dodaj], sock_out)
                            okno = "radio"

            #przycisk cofnij
            if 410 <= mouse[0] <= 460 and 100 <= mouse[1] <= 150:
                pygame.draw.rect(screen, navy_blue_light, przycisk_cofnij, border_radius=3)
            else:
                pygame.draw.rect(screen, navy_blue, przycisk_cofnij, border_radius=3)
            text = font.render("Cofnij", True, white)
            textRect = text.get_rect()
            textRect.center = przycisk_cofnij.center
            screen.blit(text, textRect)

            #przycisk gora
            if 350 <= mouse[0] <= 390 and 45 <= mouse[1] <= 85:
                pygame.draw.rect(screen, navy_blue_light, przycisk_gora, border_radius=3)
            else:
                pygame.draw.rect(screen, navy_blue, przycisk_gora, border_radius=3)
            pygame.draw.polygon(screen, white, ((przycisk_gora.centerx - 10, przycisk_gora.centery + 10),
                                                (przycisk_gora.centerx + 10, przycisk_gora.centery + 10),
                                                (przycisk_gora.centerx, przycisk_gora.centery - 10)))

            #przycisk dol
            if 350 <= mouse[0] <= 390 and 165 <= mouse[1] <= 205:
                pygame.draw.rect(screen, navy_blue_light, przycisk_dol, border_radius=3)
            else:
                pygame.draw.rect(screen, navy_blue, przycisk_dol, border_radius=3)
            pygame.draw.polygon(screen, white, ((przycisk_dol.centerx - 10, przycisk_dol.centery - 10),
                                                (przycisk_dol.centerx + 10, przycisk_dol.centery - 10),
                                                (przycisk_dol.centerx, przycisk_dol.centery + 10)))

            #przycisk wysyłania
            if 345 <= mouse[0] <= 395 and 100 <= mouse[1] <= 150:
                pygame.draw.rect(screen, navy_blue_light, przycisk_wyslij, border_radius=3)
            else:
                pygame.draw.rect(screen, navy_blue, przycisk_wyslij, border_radius=3)
            pygame.draw.polygon(screen, green, ((przycisk_wyslij.centerx - 15, przycisk_wyslij.centery - 15),
                                                (przycisk_wyslij.centerx - 15, przycisk_wyslij.centery + 15),
                                                (przycisk_wyslij.centerx + 15, przycisk_wyslij.centery)))

            for i in range(len(lista_do_wyslania)):
                text = font.render(lista_do_wyslania[i], True, black)
                textRect = text.get_rect()
                textRect.center = (100 , (Y//2 + i * 30) - (ktore_dodaj * 30))
                screen.blit(text, textRect)

            if okno == "radio":
                ktore_dodaj = 0
                flaga = True
                screen.fill(yellow)
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



