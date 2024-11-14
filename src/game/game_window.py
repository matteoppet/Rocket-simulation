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
        self.offset.x = ROCKET.body.position[0] - self.half_width
        self.offset.y = ROCKET.body.position[1] - self.half_height

        ROCKET.render(self.display_surface, self.offset)
        ENVIRONMENT.render(self.display_surface, self.offset)


class Simulation:
    def __init__(self):
        self.track = False
        self.WINDOW_SIZE = (1800, 1000)

        self.FLAGS = DOUBLEBUF
        self.screen = None


    def restart(self, launch_pad_settings):
        self.launch_pad_settings = launch_pad_settings
        self.run()

    
    def run(self):
        pygame.init()
        
        if not self.screen:
            self.screen = pygame.display.set_mode(self.WINDOW_SIZE, self.FLAGS)
            self.clock = pygame.time.Clock()
            pygame.font.init()
            pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

            self.ENVIRONMENT = Environment(self.WINDOW_SIZE)
            self.ENVIRONMENT.create_environment(self.launch_pad_settings)
            self.ROCKET = Rocket()
            self.CAMERA = Camera()

            self.ROCKET.restart(
                self.launch_pad_settings,
                pygame.Vector2(self.ENVIRONMENT.launch_pad.centerx, self.ENVIRONMENT.launch_pad.topleft[1]),
                self.ENVIRONMENT
            )
        
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        if self.track: self.track = False
                        else: self.track = True

            self.screen.fill("white")
            
            if self.track: self.CAMERA.render(self.ROCKET, self.ENVIRONMENT)
            else:
                self.ENVIRONMENT.render(self.screen, None)
                self.ROCKET.render(self.screen, None)

            timestep = self.clock.tick(60)/1000.0
            self.ROCKET.controls()
            self.ROCKET.launch(timestep)
            self.ROCKET.collision(self.ENVIRONMENT.ground_sprites)

            pygame.display.set_caption(str(round(self.clock.get_fps(), 2)))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.display.quit()
        self.screen = None
    