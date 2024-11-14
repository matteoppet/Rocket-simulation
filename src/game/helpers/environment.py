import pygame
import json

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

        self.wind_speed = environment_config[self.current_planet]["wind"]
        self.wind_angle = environment_config[self.current_planet]["wind"]

        self.gravity = environment_config[self.current_planet]["gravity"]
        self.air_density = environment_config[self.current_planet]["air density"]

        self.temperature = environment_config[self.current_planet]["temperature"]

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

            screen.blit(object.image, object_pos)

    @property
    def get_gravity(self): # TODO 
        return self.gravity
    @property
    def get_air_density(self): # TODO
        return self.air_density
    @property
    def get_wind_speed(self):
        return self.wind_speed
    @property
    def get_wind_angle(self):
        return self.wind_angle