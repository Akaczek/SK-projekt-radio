#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <arpa/inet.h>
#include <fcntl.h> // for open
#include <unistd.h> // for close
#include <pthread.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <thread>

#define FILEBUFSIZE 8192
#define SOCKBUFSIZE 4096
#define COMBUFSIZE 64

using namespace std;

chrono::milliseconds wait(10);

char file_buff[FILEBUFSIZE];
char sock_buff[SOCKBUFSIZE];
char com_buff[COMBUFSIZE];

typedef struct sock{
  	int out;
  	int kom;
  }sock;

vector<string> listaplikow;
vector<sock> clientFds;

int ile_klientow = 0;
int ile_plikow = 0;


//odbieranie od klienta
void * odbierz_dane(void *arg)
{
  	cout << "Nowy sluchacz" << endl;
  	int sock = *((int *)arg);
  	int n;
  	
  	//odebranie nazwy pliku
  	while(1){
  		n = recv(sock, sock_buff, SOCKBUFSIZE, MSG_DONTWAIT);
  		if(n == 0){
  			close(sock);
  			break;
  		}
  		if(n > 0){
  			cout << "Odbior pliku od sluchacza" << endl;
  			listaplikow.push_back(sock_buff);
			ofstream lista("listaplikow", ios_base::app);
			lista << sock_buff;
			lista << endl;
			lista.close();
  			
  			ofstream file(sock_buff, ios::binary);
  			memset(&sock_buff, 0, sizeof (sock_buff));
  	
  		//odebranie zawartosci pliku
  			while(1){
  				n = recv(sock , sock_buff , SOCKBUFSIZE , 0);
				if(n == 6){
					break;
				}
				if(n > 0){
					file.write(sock_buff, n);
					memset(&sock_buff, 0, sizeof (sock_buff));
				}	
				if(n == 0)
					break;
				this_thread::sleep_for(wait);
			}
	
    		file.close();
    		cout << "Plik odebrany" << endl;
    		ile_plikow++;
    		}
    	}
    	cout << "Sluchacz sie rozlaczyl" << endl;

    	pthread_exit(NULL);
}

void sendAudio(int sock, char* audio){
	send(sock, audio, FILEBUFSIZE,0);
}

void * zczytaj(void *)
{
	int n;
	int pauza = 0;
	int ile_zmiana = 0;
	int co_usun = 0;
	bool czy_zmiana = false;
	cout << "RADIO zaczyna nadawac" << endl;
	while (1)
	{
		int licznik_pliki = 0;
		while(licznik_pliki < ile_plikow){
			//wyslanie zawartosci pliku
			ifstream file (listaplikow[licznik_pliki], ios::binary);
			memset(&file_buff, 0, sizeof (file_buff));
			while(file){
				file.read(file_buff, FILEBUFSIZE);
				size_t count =  file.gcount();
				int licznik_klienci = 0;
				while(licznik_klienci < ile_klientow){
					send(clientFds[licznik_klienci].out, file_buff, FILEBUFSIZE,0);
					memset(&com_buff, 0, sizeof (com_buff));
					n = recv(clientFds[licznik_klienci].kom, com_buff, COMBUFSIZE, MSG_DONTWAIT);
					if(n > 0){
						if (strcmp(com_buff, "close") == 0){
							close(clientFds[licznik_klienci].out);
							close(clientFds[licznik_klienci].kom);
							clientFds.erase(clientFds.begin() + licznik_klienci);
							ile_klientow --;
							break;
						}
						if (strcmp(com_buff, "lista") == 0){
							for(int k = 0; k < ile_plikow;k++){
								const char* nazwa_pliku;
								nazwa_pliku = &listaplikow[k][0];
								send(clientFds[licznik_klienci].kom, nazwa_pliku, strlen(nazwa_pliku), 0);
								send(clientFds[licznik_klienci].kom, "|", 1, 0);
								
								this_thread::sleep_for(wait);
							}
						}
						if (strcmp(com_buff, "zmiana") == 0){
							memset(&com_buff, 0, sizeof (com_buff));
							recv(clientFds[licznik_klienci].kom, com_buff, COMBUFSIZE, 0);
							ile_zmiana = atoi(com_buff);
							ile_zmiana = ile_zmiana - licznik_pliki;
							czy_zmiana = true;
							break;
						}
						if (strcmp(com_buff, "usun") == 0){
							memset(&com_buff, 0, sizeof (com_buff));
							recv(clientFds[licznik_klienci].kom, com_buff, COMBUFSIZE, 0);
							co_usun = atoi(com_buff);
							if((licznik_pliki - co_usun) != 0){
								listaplikow.erase(listaplikow.begin() + co_usun);
								ile_plikow--;
							}
						}
					}
					if(n == 0){
						close(clientFds[licznik_klienci].out);
						close(clientFds[licznik_klienci].kom);
						clientFds.erase(clientFds.begin() + licznik_klienci);
						ile_klientow --;
						cout << "Sluchacz sie rozlaczyl" << endl;
						break;
					}
					licznik_klienci++;
				}
				if(!count)
					break;
				if(czy_zmiana == true){
					licznik_pliki = licznik_pliki + ile_zmiana;
					break;
				}
				pauza++;
				if(pauza == 28){
					sleep(1);
					pauza = 0;
				}
				
				this_thread::sleep_for(wait);
			}
			file.close();
			if(czy_zmiana == true){
				czy_zmiana = false;
			}
			else{
				licznik_pliki++;
			}		
		}
	}
	pthread_exit(NULL);
}

int main(int argc, char** argv){	

	auto port = 8001;
	int serverSocket, sock_in;
  	struct sockaddr_in serverAddr;
  	struct sockaddr_storage serverStorage;
  	socklen_t addr_size;
  	sock socks;
	string nazwa;
	pthread_t thread_id;
    	pthread_t thread_idRad;
    	
    	if(argc != 2){
    		cout << "Port ustawiony na domyslny" << endl;
    	}
    	else{
    		port = atoi(argv[1]);
    	}
	
	//Zczytanie plikow jakie znajduja sie na serwerze
	ifstream lista("listaplikow");
	while(getline(lista, nazwa)){
		listaplikow.push_back(nazwa);
		ile_plikow++;
	}
	lista.close();
	
  	
  	//Stworzenie gniazda
  	serverSocket = socket(PF_INET, SOCK_STREAM, 0);

  	//Ustawienie na IPv4 
  	serverAddr.sin_family = AF_INET;

  	//Ustawienie numeru portu
  	serverAddr.sin_port = htons(port);

  	//Ustawienie adresu na localhost
  	serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);

  	//Połączenie struktury adresu z gniazdem
  	bind(serverSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));

  	//Nasłuchiwanie na gnieździe
  	if(listen(serverSocket,20)==0)
    		printf("Czekam na polaczenie\n");
  	else
    		printf("blad: listen\n");    	
    	
    	//Stworzenie watku radia
    	if(pthread_create(&thread_idRad, NULL, zczytaj, 0) != 0)
    		printf("Nie udalo sie stworzyc watku radia\n");

    	while(1)
    	{
        	//Przyjęcie nowego połączenia
        	addr_size = sizeof serverStorage;
        	sock_in = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        	socks.out = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        	socks.kom = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        	ile_klientow++;
        	
        	//Stworzenie watku odbierajacego pliki dla nowopolaczonego klienta
        	if(sock_in> 0){
			clientFds.push_back(socks);
			if( pthread_create(&thread_id, NULL, odbierz_dane, &sock_in) != 0 )  
		   		printf("Nie udalo sie stworzyc watku odbierajacego\n");
		   		
		pthread_detach(thread_id);
		pthread_join(thread_id, NULL);

        	}
    	}
    	pthread_detach(thread_idRad);
  return 0;
}
