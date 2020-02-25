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
#include <vector>
#include <sstream>
#include <thread>

using namespace std;

int port_start_speech = PortNumber_start_speech_1;
int port_end_speech = PortNumber_end_speech_1 ;





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
  saddr.sin_port = htons(PortNumber_start);        /* for listening */
  
  if (bind(fd, (struct sockaddr *) &saddr, sizeof(saddr)) < 0)
    report("bind", 1); /* terminate */
	
  /* listen to the socket */
  if (listen(fd, MaxConnects) < 0) /* listen for clients, up to MaxConnects */
    report("listen", 1); /* terminate */

  //fprintf(stderr, "Listening on port %i for clients...\n", PortNumber_start);
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
   //cout<<"before read\n";
   int count = read(client_fd, buffer, sizeof(buffer));
   //cout<<"after read\n";
   if (count > 0) {
       //cout<<" ... \n";
   }
   close(client_fd); /* break connection */
   close(fd);
   return;
}

string wait_for_payload(){
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
  saddr.sin_port = htons(PortNumber_alexa_response);        /* for listening */
  
  if (bind(fd, (struct sockaddr *) &saddr, sizeof(saddr)) < 0)
    report("bind", 1); /* terminate */
	
  /* listen to the socket */
  if (listen(fd, MaxConnects) < 0) /* listen for clients, up to MaxConnects */
    report("listen", 1); /* terminate */

  //fprintf(stderr, "Listening on port %i for clients...\n", port_end_speech);
  /* a server traditionally listens indefinitely */
   struct sockaddr_in caddr; /* client address */
   unsigned int len = sizeof(caddr);  /* address length could change */
   
   int client_fd = accept(fd, (struct sockaddr*) &caddr, &len);  /* accept blocks */
   if (client_fd < 0) {
     report("accept", 0); /* don't terminated, though there's a problem */
   }

   /* read from client */
   int i;
   char buffer[4096];
   memset(buffer, '\0', sizeof(buffer)); 
   //cout<<"before read\n";
   unsigned int timeout =  1000;
   setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof timeout);
   int count = read(client_fd, buffer, sizeof(buffer));
   //cout<<"after read\n";
   if (count > 0) {
       //cout<<" ... \n";
   }else{
       close(client_fd); /* break connection */
       close(fd);
       return "";
   }
   string  cmd = string (buffer,count+1);  
   close(client_fd); /* break connection */
   close(fd);
   return cmd;
}
string  wait_for_speech_recognition_done(){
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
  saddr.sin_port = htons(port_end_speech);        /* for listening */
  
  if (bind(fd, (struct sockaddr *) &saddr, sizeof(saddr)) < 0)
    report("bind", 1); /* terminate */
	
  /* listen to the socket */
  if (listen(fd, MaxConnects) < 0) /* listen for clients, up to MaxConnects */
    report("listen", 1); /* terminate */

  //fprintf(stderr, "Listening on port %i for clients...\n", port_end_speech);
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
   //cout<<"before read\n";
   int count = read(client_fd, buffer, sizeof(buffer));
   //cout<<"after read\n";
   if (count > 0) {
       //cout<<" ... \n";
   }else{
       close(client_fd); /* break connection */
       close(fd);
       return "";
   }
   string cmd = string (buffer,count+1); 
   if(cmd.find('.')<cmd.size()){
   	cmd.erase(cmd.find('.'));
   }
   if(cmd.find('?')<cmd.size()){
   	cmd.erase(cmd.find('?'));
   }
   if(cmd.find('!')<cmd.size()){
   	cmd.erase(cmd.find('!'));
   }
   close(client_fd); /* break connection */
   close(fd);
   return cmd;
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
  saddr.sin_port = htons(PortNumber_MegaMindEngine); /* port number in big-endian */
  
  if (connect(sockfd, (struct sockaddr*) &saddr, sizeof(saddr)) < 0)
    report("connect", 1);
  
  /* Write some stuff and read the echoes. */ 
  if (write(sockfd, cmd.c_str(), strlen(cmd.c_str())+1) > 0) {
    /* get confirmation echoed from server and print */
    //cout<<"successful write\n";
  }
  //puts("Client done, about to exit...");
  close(sockfd); /* close the connection */
   return;
}
void start_speech_recognition(){

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
  saddr.sin_port = htons(port_start_speech); /* port number in big-endian */
  
  if (connect(sockfd, (struct sockaddr*) &saddr, sizeof(saddr)) < 0)
    report("connect", 1);
  
  /* Write some stuff and read the echoes. */ 
  char buffer[128] = "start";
  if (write(sockfd, buffer, strlen(buffer)+1) > 0) {
    /* get confirmation echoed from server and print */
    //cout<<"successful write\n";
  }
  //puts("Client done, about to exit...");
  close(sockfd); /* close the connection */
   return;
}
void payload_thread(){
while(1){
     string  payload;
     payload = wait_for_payload();    
     //cout<< "the response payload is:" <<payload <<"\n" ;
     vector <string> tokens;
     stringstream check1(payload);
     string intermediate;
     while(getline(check1, intermediate, '\"')) 
    { 
        tokens.push_back(intermediate); 
    } 
    for(int i = 0; i < tokens.size()-2; i++){
        if(tokens[i] == "caption")
        	cout << "response is:\n " <<tokens[i+2] << '\n'; 	
        if(tokens[i] == "token")
        	cout <<"token is:\n " <<tokens[i+2] << '\n'; 	
    
    }
}
}
string mode_check_callback(string cmd){
    if( ( cmd.find("go to") == string::npos) && ( cmd.find("Go to") == string::npos) ){    
	return cmd;
    }else if( cmd.find("performance") != string::npos){
        cout<<"\n++++++++++++++++++++++++++++++\n";
//        cout<<"++++++++++++++++++++++++++++++++\n";
        cout<<"+ mode changed to performance  +\n";
//        cout<<"++++++++++++++++++++++++++++++++\n";
        cout<<"++++++++++++++++++++++++++++++++\n";
	port_start_speech = PortNumber_start_speech_1;
	port_end_speech = PortNumber_end_speech_1;
        return "";
    }else if ( cmd.find("text") != string::npos){
        cout<<"\n++++++++++++++++++++++++++++++++\n";
//        cout<<"++++++++++++++++++++++++++++++++\n";
        cout<<"+++   mode changed to Text    +++ \n";
        cout<<"++++++++++++++++++++++++++++++++\n";
//        cout<<"++++++++++++++++++++++++++++++++\n";
	port_start_speech = PortNumber_start_speech_2;
	port_end_speech = PortNumber_end_speech_2 ;
        return "";
    }
    return "";
}
int main(){
  cout<<"Welcome to MegaMind Engine\n";
  thread th1(payload_thread);
  while(1){
     string cmd; 
     wait_for_keyword_detection();
     //cout << "Keyword detection recieved\n";
     start_speech_recognition();
     cmd = wait_for_speech_recognition_done();    
     cmd.erase(remove(cmd.begin(), cmd.end(), '\n'), cmd.end());
     cout << "\n\n\n==================================================\n";
     cout << "Your command is:\n "<<cmd<<"\n\n"; 
     cmd = mode_check_callback(cmd);

     send_cmd_to_sdk(cmd);
  } 

}
