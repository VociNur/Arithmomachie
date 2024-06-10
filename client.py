import multiprocessing
import socket
from threading import Thread
import time

from enums.TypeMessage import TypeMessage
from main import Game
from match import Match
from minmax import Minmax
import platform

class Client:


    def __init__(self) -> None:
        self.client_program()

    def fake_match(self, match: Match):
        print("Doing", match.to_string())
        time.sleep(0.3)
        result = 1
        match.result = result

        return match
        
    def do_match(self, match : Match):
        turns = 4000
        depth = 1

        game = Game()
        time.sleep(1)
        for i in range(turns):
            if not self.is_connected:
                break
            coups = game.get_game_available_moves()
            if len(coups) == 0 or game.winner != -1:
                break
            eval_fct = match.ev1.evaluate if i % 2 == 0 else match.ev2.evaluate
            points, moves, move = Minmax().min_max(game, depth, eval_fct)
            game.play_move(move)
        match.result = game.winner
        return match

    def play_match_and_send_result(self, match: Match):
        if platform.uname().node == "jules-ThinkPad-X1-Yoga-Gen-7" or platform.uname().node == "DESKTOP-FSB75IP":
            match = self.fake_match(match)
        else:
            match = self.do_match(match)

        if self.is_connected:
            self.client_socket.send(match.to_packet())
        pass

    def client_program(self):
        #home
        host = "109.215.159.203"  # as both code is running on same pc

        #local
        if platform.uname().node == "jules-ThinkPad-X1-Yoga-Gen-7":
                host = socket.gethostname()

        #l
        #host = "10.0.2.15"
        print(host)


        port = 49300  # socket server port number

        self.client_socket = socket.socket()  # instantiate
        
        
        self.is_connected = False
        while not self.is_connected:
            print("Connecting...")
            try:
                self.client_socket.connect((host, port))  # connect to the server
                self.is_connected = True
            except:
                print("Cannot connect now : Any server")
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
            while self.is_connected:
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
                        self.is_connected = False

                        print("close connection by server")
                    if type_data == TypeMessage.MATCH:
                        print("Get match")
                        match = Match.from_string(data)
                        t = Thread(target = self.play_match_and_send_result, args=(match,))
                        t.start()
                        threads.append(t)
                    
        
                        
        finally:
            print("Finally")
            self.client_socket.close()  # close the connection

        


def old_main():
    while True:
        print("relaunch")
        try:
            Client()
            time.sleep(10)
        finally:
            print("relaunching")



def run_client():
    while True:
        print("relaunch")
        try:
            Client()
            time.sleep(10)
        finally:
            print("relaunching")


if __name__ == '__main__':
    processes = []

    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=run_client)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
