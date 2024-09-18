import pygame
from python_scripts.camera import Camera
from python_scripts.rocket import Rocket
from environment import Environment
from settings import *


class Simulation:
    def __init__(self, screen):
        self.clock = pygame.time.Clock()

        self.screen = screen
        self.ROCKET = Rocket()
        self.environment = Environment((WINDOW_WIDTH, WINDOW_HEIGHT))


    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.screen.fill("#009bff")
            self.screen_handling()

            pygame.display.flip()
            self.clock.tick(60)


    def screen_handling(self):
        dt = self.clock.tick(60)/1000.0
        self.ROCKET.controls()
        self.ROCKET.current_state(self.environment, self.environment.current_world, dt)
        self.ROCKET.update_position_angle_rocket(dt)
        self.ROCKET.collision(self.environment.rects_environment["platform"])
        self.ROCKET.render(self.screen)

        self.environment.render_water(self.screen)
        self.environment.render_platform(self.screen)