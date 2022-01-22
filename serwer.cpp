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

vector<string> listaplikow;
vector<int> clientFds;

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

typedef struct sock{
  	int out;
  	int in;
  }sock;

//odbieranie od klienta
void * odbierz_dane(void *arg)
{
  	cout << "Nowy klient" << endl;
  	int sock = *((int *)arg);
  	int n;
  	
  	//odebranie nazwy pliku
  	cout << "Odbior pliku" << endl;
  	recv(sock, sock_buff, SOCKBUFSIZE, 0);
  	
  	ofstream file(sock_buff, ios::binary);
  	memset(&sock_buff, 0, sizeof (sock_buff));
  	
  	//odebranie zawartosci pliku
  	while(1){
  		n = recv(sock , sock_buff , SOCKBUFSIZE ,MSG_DONTWAIT);
		if(n > 0){
			
			file.write(sock_buff, n);
			memset(&sock_buff, 0, sizeof (sock_buff));
		}
		if(n == 0)
			break;
	}
	
    	file.close();
    	cout << "Plik odebrany" << endl;
    	cout << "wyjscie z watku" << endl;

    	pthread_exit(NULL);
}

void sendAudio(int sock, char* audio){
	send(sock, audio, FILEBUFSIZE,0);
}

void * zczytaj(void *arg)
{
	cout << "RADIO" << endl;
	ifstream file ("nowykolor", ios::binary);
  	memset(&file_buff, 0, sizeof (file_buff));
  	
  	//wyslanie zawartosci pliku
  	while(file){
  		file.read(file_buff, FILEBUFSIZE);
  		size_t count =  file.gcount();
  		for(size_t i = 0; i < clientFds.size(); i++)
  			sendAudio(clientFds[i], file_buff);
  		if(!count)
  			break;
  		this_thread::sleep_for(wait);
  	}
  	
    	file.close();
	pthread_exit(NULL);
}

int main(){
	int serverSocket, newSocket;
  	struct sockaddr_in serverAddr;
  	struct sockaddr_storage serverStorage;
  	socklen_t addr_size;

	

  	sock socks;
  	//Stworzenie gniazda
  	serverSocket = socket(PF_INET, SOCK_STREAM, 0);

  	//Ustawienie na IPv4 
  	serverAddr.sin_family = AF_INET;

  	//Ustawienie numeru portu
  	serverAddr.sin_port = htons(4444);

  	//Ustawienie adresu na localhost
  	serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);


  	//Set all bits of the padding field to 0
  	// memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);

  	//Połączenie struktury adresu z gniazdem
  	bind(serverSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));

  	//Nasłuchiwanie na gnieździe
  	if(listen(serverSocket,50)==0)
    		printf("Czekam na polaczenie\n");
  	else
    		printf("blad: listen\n");
    	pthread_t thread_id;
    	pthread_t thread_idRad;
    	
    	if(pthread_create(&thread_idRad, NULL, zczytaj, 0) != 0)
    		printf("Nie udalo sie stworzyc watku radia\n");

    	while(1)
    	{
        	//Przyjęcie nowego połączenia
        	addr_size = sizeof serverStorage;
        	socks.in = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        	socks.out = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        	cout << socks.out << endl;
        	if(socks.in > 0){
			clientFds.push_back(socks.out);
			if( pthread_create(&thread_id, NULL, odbierz_dane, &socks.in) != 0 )  
		   		printf("Nie udalo sie stworzyc watku odbierajacego\n");

			pthread_detach(thread_id);
			pthread_join(thread_id,NULL);
        	}
    	}
    	pthread_detach(thread_idRad);
    	pthread_mutex_destroy(&lock);
  return 0;
}
