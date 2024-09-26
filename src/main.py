if __name__ == "__main__":
    import pygame
    from simulation import Simulation
    from settings import *

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    pygame.font.init()

    SIMULATION = Simulation(screen)
    SIMULATION.run()