import pygame
from helpers.rocket import Rocket
from helpers.environment import Environment
from helpers.setup_simulation import Setup
from settings import *

import time

class Simulation:
    def __init__(self, screen):
        self.screen = screen

        self.clock = pygame.time.Clock()

        self.ROCKET = Rocket()
        self.ENVIRONMENT = Environment((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.SETUP = Setup((WINDOW_WIDTH, WINDOW_HEIGHT), self.ROCKET)

        self.current_screen = "setup"


    def run(self):
        """Run the UI to make the setup"""        
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                

                # if in setup window
                if self.current_screen == "setup":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos_mouse = pygame.mouse.get_pos()
                        # edit current variable
                        self.SETUP.check_event_edit_variable(pos_mouse)

                        # launch button
                        if self.SETUP.buttons["launch"].collidepoint(pos_mouse):
                            status_list = [dict_values["status"] for dict_values in self.SETUP.buttons["launch status check"].values()]

                            if all(status_list):
                                self.ROCKET.set_parameters(self.SETUP.rocket_settings, self.SETUP.environment_settings, self.SETUP.engine_settings, self.SETUP.mission_settings)
                                self.ROCKET.reset()
                                self.current_screen = "simulation"

                        # create stage button
                        if self.SETUP.buttons["add_stage"].collidepoint(pos_mouse):
                            if self.SETUP.id_count_stages < 7:
                                self.SETUP.id_count_stages += 1
                                self.SETUP.current_stage_to_show = self.SETUP.id_count_stages
                                # system this
                                self.SETUP.rocket_settings[self.SETUP.id_count_stages] = {
                                        "dry mass": {"value": 0, "rect": ..., "type": "kg"},
                                        "propellant mass": {"value": 0, "rect": ..., "type": "kg"},
                                        "cd": {"value": 0.1, "rect": ..., "type": ""}
                                    }
                                self.SETUP.engine_settings[self.SETUP.id_count_stages] = {
                                        "engine identifier": {"value": "Default", "rect": ..., "type": ""},
                                        "thrust power": {"value": 100, "rect": ..., "type": "N"},
                                        "ISP": {"value": 300, "rect": ..., "type": "s"},
                                        "thrust vector angle": {"value": 0, "rect": ..., "type": "°"},
                                        "number engines": {"value": 1, "rect": ..., "type": ""}
                                    }

                        # delete stage
                        if self.SETUP.buttons["delete_stage"].collidepoint(pos_mouse):
                            if self.SETUP.id_count_stages > 1:
                                self.SETUP.rocket_settings.popitem()
                                self.SETUP.engine_settings.popitem()

                                self.SETUP.id_count_stages -= 1

                                if self.SETUP.current_stage_to_show > 1:
                                    self.SETUP.current_stage_to_show -= 1

                        # edit stage
                        for number_stage, rect in self.SETUP.buttons["edit_stage"].items():
                            if rect.collidepoint(pos_mouse) and number_stage != self.SETUP.current_stage_to_show:
                                self.SETUP.current_stage_to_show = number_stage

                        # launch status check
                        for monitor, values in self.SETUP.buttons["launch status check"].items():
                            if values['rect'].collidepoint(pos_mouse):
                                self.SETUP.validation_monitor(monitor)


                    if event.type == pygame.KEYDOWN:
                        self.SETUP.edit_variable(event)
 
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
        self.SETUP.run(self.screen, self.clock)
