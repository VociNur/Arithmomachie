import socket
import threading
from time import time
from typing import List

from computer import Computer
from match import Match

class MyServer:
    
    def __init__(self, nbr_listener) -> None:
        self.message_separator = "|"
        self.match_to_play : List[Match] = []
        self.current_matches : List[Match]= []
        self.result = []

        self.connected_computers : List[Computer]= []
        self.threads : List[threading.Thread] = []
        self.running = True

        # get the hostname
        self.host = socket.gethostname()
        self.port = 5000 # initiate port no above 1024

        self.server_socket = socket.socket()  # get instance
        # look closely. The bind() function takes tuple as argument
        self.server_socket.bind((self.host, self.port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        self.server_socket.listen(nbr_listener)
        self.server_program()

    def command(self):
        while self.running:
            mes = input("->")
            if mes == "show":
                print("--- Connected computer ---")
                for c in self.connected_computers:
                    print(c)
                print("--------------------------")
            if mes == "matches" or mes == "m":
                print("------ Match to play ------")
                for m in self.match_to_play:
                    print(m)
                print("----- Playing matches -----")
                for c in self.connected_computers:
                    c.print_match()
                print("--------------------------")
            if mes == "shutdown" or mes == "s":
                self.running = False
                self.server_socket.sendall("bye".encode())

                client_socket = socket.socket()  # instantiate
                client_socket.connect((self.host, self.port))  # connect to the server
                client_socket.close() #juste pour actualiser
                time.sleep(1)
                self.server_socket.close()
                print("Shutdown...")

    def on_new_client(self, conn:socket, addr):
        print("Connection from: " + str(addr))
        
        mes = conn.recv(1024).decode()
        
        smes = mes.split(",")
        if len(smes) != 3:
            return
        system, node_name, cores_number = smes
        computer = Computer(conn, addr)
        computer.set_stat(system, node_name, cores_number)
        print("Connected:", str(computer))
        self.connected_computers.append(computer)
        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                # if data is not received break
                break
            print("from " + str(addr) + ":" + str(data))
        print("close connection")
        self.connected_computers.remove(computer)    
        conn.close()  # close the connection


    def wait_client(self):
        
        while self.running:
            conn, addr = self.server_socket.accept()
            t = threading.Thread(target = self.on_new_client, args = [conn, addr])
            t.start()
            self.threads.append(t)


    def server_program(self):



        #Permet d'effectuer des commandes
        t = threading.Thread(target = self.command)
        t.start()
        self.threads.append(t)

        #Permet d'attendre des clients
        clients = threading.Thread(target= self.wait_client)
        clients.start()
        self.threads.append(clients)

        
        print("Finishing")
        return
        while True:
            pass
        
        for c in self.connected_computers:
            c.conn.close()
        for t in self.threads:
            t.join()
        print("Finished !")


if __name__ == '__main__':
    MyServer(2)
    while True:
        time.sleep(10)