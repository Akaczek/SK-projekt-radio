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

#define BUFSIZE 15000

using namespace std;

char client_message[BUFSIZE];
char buffer[32];

FILE *out;

int ile = 0;
unordered_set<int> clientFds;

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

//odbieranie od klienta
void * socketThread(void *arg)
{
  	cout << "Nowy watek" << endl;
  	int newSocket = *((int *)arg);
  	int n;
  	//odebranie nazwy pliku
  	recv(newSocket, client_message, BUFSIZE, 0);
  	
  	ofstream file(client_message, ios::binary);
  	memset(&client_message, 0, sizeof (client_message));
  	
  	//odebranie zawartosci pliku
  	while(1){
  		n = recv(newSocket , client_message , BUFSIZE ,MSG_DONTWAIT);
		if(n > 0){
			
			file.write(client_message, n);
			cout << "write poszedl" <<  endl;
			memset(&client_message, 0, sizeof (client_message));
		}
		if(n == 0)
			break;
	}

    	file.close();
    	cout << "wyjscie z watku" << endl;

    	pthread_exit(NULL);
}

int main(){
  int serverSocket, newSocket;
  struct sockaddr_in serverAddr;
  struct sockaddr_storage serverStorage;
  socklen_t addr_size;

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
        newSocket = accept(serverSocket, (struct sockaddr *) &serverStorage, &addr_size);
        clientFds.insert(newSocket);
        

        if( pthread_create(&thread_id, NULL, socketThread, &newSocket) != 0 )  
           printf("Nie udalo sie stworzyc watku\n");

        pthread_detach(thread_id);
        pthread_join(thread_id,NULL);
    }
  return 0;
}
