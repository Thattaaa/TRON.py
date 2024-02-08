import pygame as pg
from tron import Bike, game_surface_xy

pg.init()

white, black, red, green, blue = pg.Color('white'), pg.Color('black'), pg.Color('red'), pg.Color('green'), pg.Color('blue')
sx, sy = (1800, 1000)
screen = pg.display.set_mode((sx, sy),pg.RESIZABLE)
go = True

game_surface = pg.Surface(game_surface_xy)
hsx, hsy = game_surface_xy[0]//2, game_surface_xy[1]//2

screenrect = screen.get_rect()
clock = pg.time.Clock()

player1 = Bike(hsx, hsy, red)
# player2 = Bike(hsx-50, hsy-50, blue)

pause = False
while go:
    dt = clock.tick(120)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            go = False
        if event.type == pg.VIDEORESIZE:
            sx,sy = event.size

    if not pause:
        if player1.collide_lines(player1):
            print("You died")
            pause = True

        player1.angle_change()
        player1.sim(dt)
    
    game_surface.fill((33,33,33))

    player1.draw(game_surface)
    
    screen.fill(black)

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

pg.quit()