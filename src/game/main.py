import pygame
from pygame.locals import *

from game.helpers.rocket import Rocket
from game.helpers.environment import Environment


class Camera:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0]//2
        self.half_height = self.display_surface.get_size()[1]//2

        self.offset = pygame.Vector2()

    def render(self, ROCKET: object, ENVIRONMENT: object) -> None:
        self.offset.x = ROCKET.position[0] - self.half_width
        self.offset.y = ROCKET.position[1] - self.half_height

        ROCKET.render(self.display_surface, self.offset)
        ENVIRONMENT.render(self.display_surface, self.offset)


class Simulation:
    def __init__(self, rocket_settings, engine_settings, environment_settings, mission_settings):
        self.rocket_settings = rocket_settings
        self.engine_settings = engine_settings
        self.environment_settings = environment_settings
        self.mission_settings = mission_settings
        self.track = False
        self.WINDOW_SIZE = (1800, 1000)

        pygame.init()
        flags = DOUBLEBUF
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE, flags)
        self.clock = pygame.time.Clock()
        pygame.font.init()
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

        self.ROCKET = Rocket()
        self.CAMERA = Camera()
        self.ENVIRONMENT = Environment(self.WINDOW_SIZE)
        self.ENVIRONMENT.create_environment(self.mission_settings)

        self.ROCKET.set_constants(
            self.rocket_settings,
            self.engine_settings,
            self.environment_settings,
            self.mission_settings,
            self.ENVIRONMENT.platform
        )
        self.ROCKET.set_variables()
        self.run()
    

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        if self.track: self.track = False
                        else: self.track = True

            self.screen.fill("white")
            
            if self.track: self.CAMERA.render()
            else:
                self.ENVIRONMENT.render(self.screen, None)
                self.ROCKET.render(self.screen, None)

            dt = self.clock.tick(60)/1000.0
            self.ROCKET.controls()
            self.ROCKET.run(dt)
            self.ROCKET.collision(self.ENVIRONMENT.ground_sprites)

            pygame.display.flip()
            self.clock.tick(60)
