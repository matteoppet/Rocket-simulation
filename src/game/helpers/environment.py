import pygame
import json
import math
import numpy as np

class Object(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, group: pygame.sprite.Group):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect
        self.image.fill("black")
        
class Environment:
    def __init__(self, window_size: tuple):
        super().__init__()
        self.window_size = window_size
        self.ground_sprites = pygame.sprite.Group()

        with open("config/environment_config.json", "r") as file:
            environment_config = json.load(file)

        self.current_planet = "planet_1"

        self.wind_speed = environment_config[self.current_planet]["wind speed"]
        self.wind_angle = environment_config[self.current_planet]["wind angle"]

        self.gravity = environment_config[self.current_planet]["gravity"]
        self.air_density = environment_config[self.current_planet]["air density"]

        self.temperature = environment_config[self.current_planet]["temperature"]
        self.radius_planet = environment_config[self.current_planet]["radius"]
        
    def create_environment(self, launch_pad_settings: dict):
        launch_pad_altitude = launch_pad_settings["elevation"]
        launch_pad_angle = launch_pad_settings["launch angle"]

        self.base_terrain = pygame.Rect(0, self.window_size[1]-10, self.window_size[0], 10)

        self.launch_pad = pygame.Rect(800, self.window_size[1]-20-launch_pad_altitude, 100, 10)

        altitude_poles = self.base_terrain.y-self.launch_pad.bottomleft[1]
        launch_pad_pole_1 = pygame.Rect(self.launch_pad.x, self.launch_pad.bottomleft[1], 10, altitude_poles)
        launch_pad_pole_2 = pygame.Rect(self.launch_pad.topright[0]-self.launch_pad.height, self.launch_pad.bottomright[1], 10, altitude_poles)

        Object(self.base_terrain, self.ground_sprites)
        Object(self.launch_pad, self.ground_sprites)
        Object(launch_pad_pole_1, self.ground_sprites)
        Object(launch_pad_pole_2, self.ground_sprites)

    def render(self, screen: pygame.Surface, offset: tuple):
        for object in self.ground_sprites:
            if offset is not None: object_pos = object.rect.topleft - offset
            else: object_pos = object.rect.topleft

            size_image = pygame.Vector2(object.image.get_size()[0], object.image.get_size()[1])
            scaled_image = pygame.transform.smoothscale(object.image, size_image)

            screen.blit(scaled_image, object_pos)

    def get_gravity(self, altitude) -> float:
        radius_planet = self.radius_planet*1000 # in meters
        gravity_at_sea_level = self.gravity
        new_gravity = gravity_at_sea_level*(radius_planet/(radius_planet+altitude))**2
        return new_gravity
    def get_air_density(self, altitude, decay_constant=0.0001) -> float: # TODO changes with altitude
        # if altitude < 100000: new_air_density = self.air_density * (1 - (altitude/100000) * 2)
        # else: new_air_density = self.air_density * (1 - (altitude/100000))
        # return new_air_density
        current_air_density = self.air_density * math.exp(-decay_constant * altitude)
        return current_air_density
    @property
    def get_wind_speed(self):
        return self.wind_speed
    @property
    def get_wind_angle(self):
        return self.wind_angle
    @property 
    def get_wind_velocity_vector(self):
        return np.array([
            self.get_wind_speed * np.sin(np.radians(self.get_wind_angle)),
            self.get_wind_speed * np.cos(np.radians(self.get_wind_angle))
        ])