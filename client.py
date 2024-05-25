import socket
from threading import Thread
import time

from enums.TypeMessage import TypeMessage
from match import Match

class Client:


    def __init__(self) -> None:
        self.client_program()

    def fake_match(self, match: Match):
        print("Doing", match.to_string())
        time.sleep(12)
        result = 1
        match.result = result
        self.client_socket.send(match.to_packet())
        


    def play_match_and_send_result(self, match: Match):
        
        #match.ev1.battle(match.ev2)
        pass

    def client_program(self):
        host = socket.gethostname()  # as both code is running on same pc
        port = 5000  # socket server port number

        self.client_socket = socket.socket()  # instantiate
        
        
        connected = False
        self.running = True
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

        threads = []

        try:
            encoded_data = ""
            while self.running:
                print("waiting")
                add_encoded_data = self.client_socket.recv(1024).decode()
                if not add_encoded_data:
                    # if data is not received break
                    break
                encoded_data = encoded_data + add_encoded_data
                print(encoded_data)
                decoded_data, encoded_data = TypeMessage.decode_package(encoded_data)
                print(decoded_data, encoded_data)
                
                for (type_data, data) in decoded_data:
                    if type_data == TypeMessage.END_CONNECTION:
                        self.running = False
                    if type_data == TypeMessage.MATCH:
                        print("Get match")
                        match = Match.from_string(data)
                        t = Thread(target = self.fake_match, args=(match,))
                        t.start()
                        threads.append(t)
        
                        
        finally:
            print("close connection")
            self.client_socket.close()  # close the connection

        


if __name__ == '__main__':
    Client()