import pygame
from math import exp

class Environment:
    def __init__(self, window_size):
        self.rects_environment = {
            "water": None,
            "platform": None
        }

        self.planets_data = {
            "earth": {
                "gravity": 9.81,
                "drag_coeff": 0.1,
                "air_density_sea_level": 1.225,
                "scale_height": 7000,
            },
        }

        self.create_water(window_size[0], 20, 0, window_size[1]-20)
        self.create_platform(150, 15, 150, window_size[1]-30)

        self.current_world = "earth"


    def update_forces(self, rocket_altitude, planet):
        current_gravity = self.planets_data[planet]["gravity"] * float((6371000 / (6371000 + rocket_altitude)) ** 2)
        current_air_density = self.planets_data[planet]["air_density_sea_level"] * exp(-rocket_altitude/self.planets_data[planet]["scale_height"])

        return current_gravity, current_air_density

    def create_water(self, width, height, x, y):
        self.rects_environment["water"] = pygame.Rect(x, y, width, height)

    def create_platform(self, width, height, x, y):
        self.rects_environment["platform"] = pygame.Rect(x, y, width, height)

    def render_water(self, screen):
        pygame.draw.rect(screen, "#acdeff", self.rects_environment["water"])

    def render_platform(self, screen):
        pygame.draw.rect(screen, "#333333", self.rects_environment["platform"])
