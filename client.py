import socket
from threading import Thread
import time

from TypeMessage import TypeMessage
from match import Match

class Client:


    def __init__(self) -> None:
        self.client_program()

    def fake_match(self, match: Match):
        print("Doing", match.to_string())
        time.sleep(10)
        result = 1
        match.result = result
        self.client_socket.send()
        


    def play_match_and_send_result(self, match: Match):
        
        #match.ev1.battle(match.ev2)
        pass

    def client_program(self):
        host = socket.gethostname()  # as both code is running on same pc
        port = 5000  # socket server port number

        self.client_socket = socket.socket()  # instantiate
        
        
        connected = False
        while not connected:
            print("Connecting...")
            try:
                self.client_socket.connect((host, port))  # connect to the server
                connected = True
            except:
                print("Cannot connect now")
                time.sleep(10)
        print("Connected !")
        
        system = ""
        node_name = ""
        cores_number = ""
        get_os = False
        get_platform = False
        try:
            import os
            cores_number = str(os.cpu_count())
            get_os = True
        except:
            pass

        try:
            import platform
            system_info = platform.uname()
            system = system_info.system
            node_name = system_info.node
            get_platform = True
        except:
            pass

        self.client_socket.send(TypeMessage.encode_package(TypeMessage.CONNECTION, system + "," + node_name + "," + cores_number))

        message = ""
        threads = []
        while message.lower().strip() != 'bye':
            message = self.client_socket.recv(1024).decode()
            if message == "bye":
                break

            match = Match.from_string(message)
            t = Thread(target = self.fake_match, args=(match,))
            t.start()
            threads.append(t)
        

        self.client_socket.close()  # close the connection
        


if __name__ == '__main__':
    Client()