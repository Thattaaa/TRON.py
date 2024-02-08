import os, socket, threading, protocol, tron
from tron import game_surface_xy
import errno
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg

white, black, red, green, blue = pg.Color('white'), pg.Color('black'), pg.Color('red'), pg.Color('green'), pg.Color('blue')

pg.init()
sx, sy = (1800, 1000)
screen = pg.display.set_mode((sx, sy),pg.RESIZABLE)
game_surface = pg.Surface(game_surface_xy)
# hsx, hsy = game_surface_xy[0]//2, game_surface_xy[1]//2
clock = pg.time.Clock()



class Networking:
    def __init__(self, Username: str, host: str = "127.0.0.1", port: int = 42069) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = Username
        self.host = host
        self.port = port
        
        self.state = protocol.State.WAITING
        self.state_lock = threading.Lock()

        self.stop = False

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            threading.Thread(target=Networking.recieveshit, args=(self, self.socket), daemon=True).start()
        except socket.error as e:
            if self.error_handle(e):
                self.stop = True
            else:
                raise e

    def recieveshit(self, conn: socket.socket) -> None:
        while not self.stop:
            try:
                data = conn.recv(1024)
            except socket.error as e:
                if self.error_handle(e):
                    self.stop = True
                    continue
                else:
                    raise e
            msg = protocol.Msg.deserialize(data)
            self.state_lock.acquire()
            self.protocol_matcher(msg)
            self.state_lock.release()

    def error_handle(self, error):
        match error.errno:
            case errno.ECONNRESET:
                print("[!] Connection Reset!\nProceeding to Cleanup...")
                return True
            case errno.ECONNREFUSED:
                print("[!] Connection Refused by Host!\nProceeding to cleanup...")
                return True
            case errno.ECONNABORTED:
                print("[!] Connection Aborted!\nProceeding to Cleanup...")
                return True
        return False


    def protocol_matcher(self, msg: protocol.Msg):
        match msg.type:
            case protocol.MsgType.GAMESTART:
                self.state = protocol.State.GAME
            case protocol.MsgType.EXIT:
                self.state = protocol.State.EXIT
            case _:
                print("UNHANDLED")

    def sendshit(self, data: bytes):
        self.socket.send(data)

    def cleanup(self):
        print("Closing...")
        self.stop = True
        self.socket.close()

a = Networking("Thatta")
a.connect()

a.sendshit(protocol.Msg(protocol.MsgType.ID, {"username": "Thatta", "colour": red}).serialize())

Player = tron.Bike(sx/2, sx/2, red)
run = True
while run:
    match a.state:
        case protocol.State.WAITING:
            continue
        
        case protocol.State.EXIT:
            run = False

        case protocol.State.GAME:


            dt = clock.tick(120)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # run = False
                    # TODO: announce exit
                    a.sendshit(protocol.Msg(protocol.MsgType.EXIT, "").serialize())
                    run = False
                if event.type == pg.VIDEORESIZE:
                    sx,sy = event.size

            Player.angle_change()
            Player.sim(dt)
            
            game_surface.fill((33,33,33))

            Player.draw(game_surface)

            game_surface.fill((33,33,33))
            screen.blit(game_surface, screen.get_rect().center)

            # viewport
            ratio_x = sx/game_surface.get_width()
            ratio_y = sy/game_surface.get_height()
            nw = game_surface.get_width()*ratio_y
            nh = game_surface.get_height()*ratio_x
            
            if nw <= sx:
                f = sx-nw
                screen.blit(pg.transform.scale(game_surface, (nw, sy)), (f/2, 0))
            else:
                f = sy-nh
                screen.blit(pg.transform.scale(game_surface, (sx, nh)), (0, f/2))
            #~ viewport

            pg.display.update()

        
a.cleanup()
pg.quit()