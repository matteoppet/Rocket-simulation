import pygame

from world import Terrain, YSortCameraGroup
from rocket import Rocket
from settings import *

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
pygame.font.init()

visible_sprites = YSortCameraGroup()
TERRAIN = Terrain(WINDOW_WIDTH, WINDOW_HEIGHT, visible_sprites)
ROCKET = Rocket(TERRAIN.position.y, visible_sprites)



TIMEREVENT = pygame.USEREVENT + 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == TIMEREVENT:
            ROCKET.t_minus += 1
            pygame.time.set_timer(TIMEREVENT, 1000)

    screen.fill(BACKGROUND_COLOR)

    # calculate delta time
    dt = clock.tick(60)/1000.0

    TERRAIN.collisions(ROCKET, TERRAIN)

    ROCKET.controls(TIMEREVENT)
    ROCKET.current_state(dt, GRAVITY, ROCKET.position)
    ROCKET.debug(screen)

    visible_sprites.custom_draw(ROCKET, TERRAIN)

    print(clock.get_fps())

    pygame.display.flip()
    clock.tick(60)


pygame.quit()