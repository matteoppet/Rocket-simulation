import pygame
from python_scripts.camera import Camera
from python_scripts.rocket import Rocket
from python_scripts.environment import Environment
from python_scripts.setup_simulation import Setup
from settings import *

import time

class Simulation:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.ROCKET = Rocket()
        self.ENVIRONMENT = Environment((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.SETUP = Setup((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.current_screen = "setup"


    def run(self):
        """Run the UI to make the setup"""        
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                
                # change screen
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.current_screen == "setup":
                            if not self.SETUP.active:
                                self.ROCKET.set_parameters(self.SETUP.variables)
                                self.ROCKET.reset()
                                self.current_screen = "simulation"
                
                        elif self.current_screen == "simulation":
                            self.current_screen = "setup"

                # if in setup window
                if self.current_screen == "setup":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.SETUP.rect_input_text.collidepoint(mouse_pos):
                            self.SETUP.active = True

                    if event.type == pygame.KEYDOWN:
                        self.SETUP.user_input_text(event)
 
            if self.current_screen == "setup":
                self.setup()
            elif self.current_screen == "simulation":
                self.simulation()

            pygame.display.flip()
            self.clock.tick(60)


    def simulation(self):
        """Run simulation with all the setup from before"""
        self.screen.fill("white")
        dt = self.clock.tick(60)/1000.0

        self.ROCKET.controls(dt)
        self.ROCKET.run(dt)
        self.ROCKET.render(self.screen)
        self.ROCKET.collision(self.ENVIRONMENT.rects_environment["platform"])


    def setup(self):
        """ Setup all variables changable by the user before start simulation
        """
        self.screen.fill("white")
        self.SETUP.run(self.screen)