import socket
from typing import List, Tuple
from match import Match
from evaluation import Evaluation


class Computer:
    def __init__(self, conn:socket, addr) -> None:
        self.conn = conn
        self.addr = addr
        self.system = ""
        self.node = ""
        self.cores = ""
        self.actual_games : List[Match] = []

    def set_stat(self, system, node, cores):
        self.system = system
        self.node = node
        self.cores = cores

    def add_match(self, match:Match):
        self.actual_games.append(match)
        self.conn.send(match.to_string().encode())
        print(f"Match {match.to_string()} sent to {self.addr}")

    def print_match(self):
        for game in self.actual_games:
            print(f"{self.addr} {game.to_string()}")

    def __str__(self) -> str:
        return f"{self.addr} {self.node} ({self.system}) [{self.cores}]"