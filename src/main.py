import pygame

from world import Floor
from rocket import Rocket
from settings import *

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
pygame.font.init()

FLOOR = Floor(WINDOW_WIDTH, WINDOW_HEIGHT)
ROCKET = Rocket(FLOOR.y)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    FLOOR.draw(screen)

    # calculate delta time
    dt = clock.tick(60)/1000.0

    ROCKET.controls()
    ROCKET.update_variables(dt, GRAVITY)
    ROCKET.debug(screen)

    ROCKET.render(screen, dt)

    pygame.display.flip()
    clock.tick(60)


pygame.quit()