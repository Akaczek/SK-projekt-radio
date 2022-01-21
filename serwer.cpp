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
#include <unordered_set>
#include <fstream>
#include <poll.h>

#define FILEBUFSIZE 4096
#define COMBUFSIZE 64

using namespace std;

char file_buff[FILEBUFSIZE];
char com_buff[COMBUFSIZE];

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
  	recv(sock, file_buff, FILEBUFSIZE, 0);
  	
  	ofstream file(file_buff, ios::binary);
  	memset(&file_buff, 0, sizeof (file_buff));
  	
  	//odebranie zawartosci pliku
  	while(1){
  		n = recv(sock , file_buff , FILEBUFSIZE ,MSG_DONTWAIT);
		if(n > 0){
			
			file.write(file_buff, n);
			memset(&file_buff, 0, sizeof (file_buff));
		}
		if(n == 0)
			break;
	}
	
    	file.close();
    	cout << "Plik odebrany" << endl;
    	cout << "wyjscie z watku" << endl;

    	pthread_exit(NULL);
}

void * wyslij(void *arg)
{
  	cout << "Nowy klient" << endl;
  	int sock = *((int *)arg);
  	int n;
  	
  	//odebranie nazwy pliku
  	cout << "Wysylanie pliku" << endl;
  	recv(sock, file_buff, FILEBUFSIZE, 0);
  	sleep(1);
  	cout << file_buff << endl;
  	ifstream file (file_buff, ios::binary);
  	memset(&file_buff, 0, sizeof (file_buff));
  	
  	//wyslanie zawartosci pliku
  	while(file){
  		file.read(file_buff, FILEBUFSIZE);
  		size_t count =  file.gcount();
  		send(sock, file_buff, FILEBUFSIZE,0);
  		memset(&file_buff, 0, sizeof (file_buff));
  		if(!count)
  			break;
  		
  	}
  	
    	file.close();
    	cout << "Plik wyslany" << endl;
    	cout << "wyjscie z watku" << endl;

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

    while(1)
    {
        //Przyjęcie nowego połączenia
        addr_size = sizeof serverStorage;
        socks.in = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        socks.out = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        if(newSocket > 0){
		
		if( pthread_create(&thread_id, NULL, odbierz_dane, &socks.in) != 0 )  
		   printf("Nie udalo sie stworzyc watku odbierajacego\n");
		if( pthread_create(&thread_id, NULL, wyslij, &socks.out) != 0 )  
		   printf("Nie udalo sie stworzyc watku wysylajacego\n");

		pthread_detach(thread_id);
		pthread_join(thread_id,NULL);
        }
    }
  return 0;
}
