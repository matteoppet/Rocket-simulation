import pygame
from helpers.rocket import Rocket
from helpers.environment import Environment
from helpers.setup_simulation import Setup
from settings import *

import math
import time

class Camera:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0]//2
        self.half_height = self.display_surface.get_size()[1]//2

        self.offset = pygame.Vector2()

    def render(self, ROCKET, ENVIRONMENT):
        self.offset.x = ROCKET.rect.centerx - self.half_width
        self.offset.y = ROCKET.rect.centery - self.half_height

        ROCKET.render(self.display_surface, self.offset)
        ENVIRONMENT.render(self.display_surface, self.offset)


class Simulation:
    def __init__(self, screen):
        self.screen = screen

        self.clock = pygame.time.Clock()

        self.ENVIRONMENT = Environment((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.ROCKET = Rocket()
        self.SETUP = Setup((WINDOW_WIDTH, WINDOW_HEIGHT), self.ROCKET)
        self.CAMERA = Camera()

        self.current_screen = "setup"

        self.trajectory_pos = []

        self.track = False


    def simulation(self):
        """Run simulation with all the setup from before"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    if self.ROCKET.current_stage < self.ROCKET.num_stages:
                        self.ROCKET.current_stage += 1
                        self.ROCKET.set_variables_based_on_current_stage()

                if event.key == pygame.K_t:
                    if self.track:
                        self.track = False
                    else:
                        self.track = True

        self.screen.fill("white")
        
        self.trajectory_pos.append(tuple(self.ROCKET.position))

        # render
        if self.track:
            self.CAMERA.render(self.ROCKET, self.ENVIRONMENT)
        else:
            # trajectory
            if len(self.trajectory_pos) > 1:
                pygame.draw.aalines(self.screen, "black", False, self.trajectory_pos)

            self.ENVIRONMENT.render(self.screen, None)
            self.ROCKET.render(self.screen, None)

        self.UI()

        # backend part
        dt = self.clock.tick(60)/1000.0
        self.ROCKET.controls()
        self.ROCKET.run(dt)
        self.ROCKET.collision(self.ENVIRONMENT.ground_sprites)

    
    def UI(self):
        # number stage
        font = pygame.font.SysFont("arial", 15)
        text_stage = font.render(str(self.ROCKET.current_stage), True, "black")
        self.screen.blit(text_stage, (10,10))


    def setup(self):
        """ Setup all variables changable by the user before start simulation
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            

            # if in setup window
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_mouse = pygame.mouse.get_pos()
                # edit current variable
                self.SETUP.check_event_edit_variable(pos_mouse)

                # launch button
                if self.SETUP.buttons["launch"].collidepoint(pos_mouse):
                    status_list = [dict_values["status"] for dict_values in self.SETUP.buttons["launch status check"].values()]

                    if all(status_list):
                        self.ENVIRONMENT.create_environment(self.SETUP.mission_settings)

                        self.ROCKET.initialize_calculation_class(
                            self.SETUP.rocket_settings, self.SETUP.engine_settings, self.SETUP.environment_settings, self.SETUP.mission_settings, self.ENVIRONMENT.platform)
                        self.current_screen = "simulation"

                # create stage button
                if self.SETUP.buttons["add_stage"].collidepoint(pos_mouse):
                    if self.SETUP.id_count_stages < 7:
                        self.SETUP.id_count_stages += 1
                        self.SETUP.current_stage_to_show = self.SETUP.id_count_stages
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

        self.SETUP.run(self.screen, self.clock)


    def run(self):
        """Run the UI to make the setup"""        
        while True:
            if self.current_screen == "setup":
                self.setup()
            elif self.current_screen == "simulation":
                self.simulation()

            pygame.display.flip()
            self.clock.tick(60)