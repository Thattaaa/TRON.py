from typing import Any
import os, socket, threading, protocol, errno
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
from time import sleep

class Network:
    def __init__(self, port: int = 42069) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.port = port
        self.players: dict[socket.socket: dict[str, Any]]  = {}
        

        self.server_socket.bind(("0.0.0.0", self.port))

        self.stop = False

        self.server_socket.listen()


    def wait_for_players(self, count):
        print(f"[+] Waiting for players... port: {self.port}")
        for _ in range(count):
            conn, addr = self.server_socket.accept()
            threading.Thread(target=Network.recieveshit, args=(self, conn), daemon=True).start()            
            print(f"[+] Connection from: {addr}")
            self.players[conn] = {}

    def cleanup(self):
        print("[!] Tidying up...")
        self.stop = True
        for conn in self.players.keys():
            conn.close()

        self.server_socket.close()

    def send(self, data: bytes):
        for conn in self.players.keys():
            conn.send(data)

    def recieveshit(self, conn: socket.socket):
        while not self.stop:
            try:
                data = conn.recv(1024)
            except socket.error as e:
                if e.errno in [errno.ECONNRESET, errno.ECONNREFUSED, errno.ECONNABORTED]:
                    self.stop = True
                else:
                    raise e
            msg = protocol.Msg.deserialize(data)
            match msg.type:
                case protocol.MsgType.ID:
                    self.players[conn] = msg.data
                    print(self.players[conn]["username"], self.players[conn]["colour"])
                case protocol.MsgType.EXIT:
                    self.stop = True
                case _:
                    print("UNHANDLED")

# on start
game = Network(42069)
game.wait_for_players(1)
players = list(game.players.values())
game.send(protocol.Msg(protocol.MsgType.GAMESTART, players).serialize())
sleep(5)
# game.send(protocol.Msg(protocol.MsgType.EXIT, "").serialize())
game.cleanup()