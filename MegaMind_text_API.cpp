#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include "sock.h"

#include <iostream>
#include <string>
#include <algorithm>
using namespace std;

void report(const char* msg, int terminate) {
  perror(msg);
  if (terminate) exit(-1); /* failure */
}

void wait_for_keyword_detection(){
   int option = 1;
  int fd = socket(AF_INET,     /* network versus AF_LOCAL */
		  SOCK_STREAM, /* reliable, bidirectional: TCP */
		  0);          /* system picks underlying protocol */
  if (fd < 0) report("socket", 1); /* terminate */
  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
  	
  /* bind the server's local address in memory */
  struct sockaddr_in saddr;
  memset(&saddr, 0, sizeof(saddr));          /* clear the bytes */
  saddr.sin_family = AF_INET;                /* versus AF_LOCAL */
  saddr.sin_addr.s_addr = htonl(INADDR_ANY); /* host-to-network endian */
  saddr.sin_port = htons(PortNumber_start_speech_2);        /* for listening */
  
  if (bind(fd, (struct sockaddr *) &saddr, sizeof(saddr)) < 0)
    report("bind", 1); /* terminate */
	
  /* listen to the socket */
  if (listen(fd, MaxConnects) < 0) /* listen for clients, up to MaxConnects */
    report("listen", 1); /* terminate */

  fprintf(stderr, "Listening on port %i for clients...\n", PortNumber_start_speech_2);
  /* a server traditionally listens indefinitely */
   struct sockaddr_in caddr; /* client address */
   unsigned int len = sizeof(caddr);  /* address length could change */
   
   int client_fd = accept(fd, (struct sockaddr*) &caddr, &len);  /* accept blocks */
   if (client_fd < 0) {
     report("accept", 0); /* don't terminated, though there's a problem */
   }

   /* read from client */
   int i;
   char buffer[BuffSize + 1];
   memset(buffer, '\0', sizeof(buffer)); 
   cout<<"before read\n";
   int count = read(client_fd, buffer, sizeof(buffer));
   cout<<"after read\n";
   if (count > 0) {
       cout<<" ... \n";
   }
   close(client_fd); /* break connection */
   close(fd);
   return;
}

void send_cmd_to_sdk(std::string cmd){

  /* fd for the socket */
  int sockfd = socket(AF_INET,      /* versus AF_LOCAL */
		      SOCK_STREAM,  /* reliable, bidirectional */
		      0);           /* system picks protocol (TCP) */
  if (sockfd < 0) report("socket", 1); /* terminate */

  /* get the address of the host */
  struct hostent* hptr = gethostbyname(Host); /* localhost: 127.0.0.1 */ 
  if (!hptr) report("gethostbyname", 1); /* is hptr NULL? */
  if (hptr->h_addrtype != AF_INET)       /* versus AF_LOCAL */
    report("bad address family", 1);
  
  /* connect to the server: configure server's address 1st */
  struct sockaddr_in saddr;
  memset(&saddr, 0, sizeof(saddr));
  saddr.sin_family = AF_INET;
  saddr.sin_addr.s_addr = 
     ((struct in_addr*) hptr->h_addr_list[0])->s_addr;
  saddr.sin_port = htons(PortNumber_end_speech_2); /* port number in big-endian */
  
  if (connect(sockfd, (struct sockaddr*) &saddr, sizeof(saddr)) < 0)
    report("connect", 1);
  
  /* Write some stuff and read the echoes. */ 
  if (write(sockfd, cmd.c_str(), strlen(cmd.c_str())+1) > 0) {
    /* get confirmation echoed from server and print */
    cout<<"successful write\n";
  }
  puts("Client done, about to exit...");
  close(sockfd); /* close the connection */
   return;
}

int main(){

  while(1){
     string cmd; 
     wait_for_keyword_detection();
     cout << "type in your request\n";
     getline(cin, cmd);
     cmd.erase(remove(cmd.begin(), cmd.end(), '\n'), cmd.end());
     cout << "your command is "<<cmd; 
     send_cmd_to_sdk(cmd);



  } 

}
