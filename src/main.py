import pygame

from python_scripts.world import General_world, Earth, YSortCameraGroup
from python_scripts.rocket import Rocket
from python_scripts.settings import *
from python_scripts.helpers import collision

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
pygame.font.init()

visible_sprites = YSortCameraGroup()
worlds_sprite = pygame.sprite.Group()
EARTH = Earth((WINDOW_WIDTH, WINDOW_HEIGHT))
ROCKET = Rocket(EARTH, visible_sprites)
 
CURRENT_PLANET = "earth"

TIMEREVENT = pygame.USEREVENT + 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == TIMEREVENT:
            ROCKET.t_minus += 1
            pygame.time.set_timer(TIMEREVENT, 1000)
        if event.type == pygame.MOUSEWHEEL:
            if event.y >= 1:
                visible_sprites.increase_decrease_zoom("increase")
            if event.y <= -1:
                visible_sprites.increase_decrease_zoom("decrease")


    visible_sprites.custom_draw(ROCKET, EARTH)

    # calculate everything
    dt = clock.tick(60)/1000.0

    ROCKET.controls(TIMEREVENT)
    ROCKET.current_state(dt)
    ROCKET.debug(screen, clock)

    # collision(ROCKET, world)


    pygame.display.flip()
    clock.tick(60)


pygame.quit()