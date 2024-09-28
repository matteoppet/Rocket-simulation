if __name__ == "__main__":
    import pygame
    from simulation import Simulation
    from settings import *
    from pygame.locals import *
    flags = DOUBLEBUF

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    clock = pygame.time.Clock()
    running = True
    pygame.font.init()
    pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    SIMULATION = Simulation(screen)
    SIMULATION.run()