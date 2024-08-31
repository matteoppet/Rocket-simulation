import pygame

from world import Floor
from rocket import Rocket
from settings import *

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True

FLOOR = Floor(WINDOW_WIDTH, WINDOW_HEIGHT)
ROCKET = Rocket(FLOOR.y)

GRAVITY = 9.81

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    FLOOR.draw(screen)
    ROCKET.draw(screen)

    ROCKET.controls()
    ROCKET.rotate()
    ROCKET.update_position(clock.tick(60)/1000.0, GRAVITY)
    ROCKET.debug()

    pygame.display.flip()
    clock.tick(60)


pygame.quit()