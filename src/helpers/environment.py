import pygame
from math import exp

class Environment:
    def __init__(self, window_size):
        self.window_size = window_size
        self.base_terrain = pygame.Rect(0, self.window_size[1]-10, self.window_size[0], 10)

    def create_environment(self, setup_dict):
        launch_altitude = setup_dict["launch altitude"]["value"]
        initial_angle = setup_dict["initial flight angle"]["value"]

        self.launch_platform_rect = pygame.Rect(800, self.window_size[1]-20-launch_altitude, 100, 10)

        altitude_poles = self.base_terrain.y-self.launch_platform_rect.bottomleft[1]
        self.launch_platform_pole_1 = pygame.Rect(self.launch_platform_rect.x, self.launch_platform_rect.bottomleft[1], 10, altitude_poles)
        self.launch_platform_pole_2 = pygame.Rect(self.launch_platform_rect.topright[0]-self.launch_platform_rect.height, self.launch_platform_rect.bottomright[1], 10, altitude_poles)

    def draw(self, screen):
        pygame.draw.rect(screen, "black", self.base_terrain)

        pygame.draw.rect(screen, "purple", self.launch_platform_rect)
        pygame.draw.rect(screen, "purple", self.launch_platform_pole_1)
        pygame.draw.rect(screen, "purple", self.launch_platform_pole_2)


    def update_forces(self, rocket_altitude, planet):
        current_gravity = self.planets_data[planet]["gravity"] * float((6371000 / (6371000 + rocket_altitude)) ** 2)
        current_air_density = self.planets_data[planet]["air_density_sea_level"] * exp(-rocket_altitude/self.planets_data[planet]["scale_height"])

        return current_gravity, current_air_density