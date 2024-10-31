import pygame
from math import exp

class Object(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, group: pygame.sprite.Group):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect
        self.image.fill("black")

class Environment:
    def __init__(self, window_size: tuple) -> None:
        self.window_size = window_size
        self.base_terrain = pygame.Rect(0, self.window_size[1]-10, self.window_size[0], 10)

        self.ground_sprites = pygame.sprite.Group()

    def create_environment(self, setup_dict: dict) -> None:
        launch_altitude = setup_dict["launch altitude"]
        initial_angle = setup_dict["initial flight angle"]

        self.platform = pygame.Rect(800, self.window_size[1]-20-launch_altitude, 100, 10)
        altitude_poles = self.base_terrain.y-self.platform.bottomleft[1]
        platform_pole_1 = pygame.Rect(self.platform.x, self.platform.bottomleft[1], 10, altitude_poles)
        platform_pole_2 = pygame.Rect(self.platform.topright[0]-self.platform.height, self.platform.bottomright[1], 10, altitude_poles)

        Object(self.platform, self.ground_sprites)
        Object(platform_pole_1, self.ground_sprites)
        Object(platform_pole_2, self.ground_sprites)
        Object(self.base_terrain, self.ground_sprites)


    def render(self, screen: pygame.Surface, offset: tuple) -> None:
        for object in self.ground_sprites:
            if offset is not None:
                object_pos_offset = object.rect.topleft - offset
            else:
                object_pos_offset = object.rect.topleft

            screen.blit(object.image, object_pos_offset)


    def update_forces(self, rocket_altitude: int, planet) -> float:
        current_gravity = self.planets_data[planet]["gravity"] * float((6371000 / (6371000 + rocket_altitude)) ** 2)
        current_air_density = self.planets_data[planet]["air_density_sea_level"] * exp(-rocket_altitude/self.planets_data[planet]["scale_height"])

        return current_gravity, current_air_density