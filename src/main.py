import pygame

from world import Earth, YSortCameraGroup
from rocket import Rocket
from settings import *

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
pygame.font.init()

visible_sprites = YSortCameraGroup()
worlds_sprite = pygame.sprite.Group()
EARTH = Earth(WINDOW_WIDTH, WINDOW_HEIGHT, [visible_sprites, worlds_sprite])
ROCKET = Rocket(EARTH, visible_sprites)
 
CURRNET_PLANET = "earth"

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

    # draw everything
    screen.fill(BACKGROUND_COLOR)

    for world in worlds_sprite:
        if world.name == CURRNET_PLANET:
            visible_sprites.custom_draw(ROCKET, world)

            # calculate everything
            dt = clock.tick(60)/1000.0

            world.collisions(ROCKET, world)
            ROCKET.controls(TIMEREVENT)
            ROCKET.current_state(dt)
            ROCKET.debug(screen)


    pygame.display.flip()
    clock.tick(60)


pygame.quit()