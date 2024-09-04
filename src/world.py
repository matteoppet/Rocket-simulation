from pygame import sprite, Rect, Surface, Vector2, display, transform
from settings import *


class World():
    def collisions(self, sprite_1, sprite_2):
        if sprite_1.rect.colliderect(sprite_2):
            if not sprite_1.on_platform:
                sprite_1.collision = True
                sprite_1.reset()


    def render(self, screen, offset, zoom_factor):
        terrain_offset_position = (self.rect.topleft - offset) * zoom_factor
        terrain_scaled_image = transform.scale(
            self.image,
            (int(self.image.get_width() * zoom_factor),
             int(self.image.get_height() * zoom_factor)))
        
        self.position = terrain_offset_position
        screen.blit(terrain_scaled_image, terrain_offset_position)


class Earth(World, sprite.Sprite):
    def __init__(self, WINDOW_WIDTH, WINDOW_HEIGHT, group):
        sprite.Sprite.__init__(self)
        super().__init__(group)

        self.name = "earth"

        # ! SPECIFICS WORLD
        self.drag_coeff = 0.1
        self.gravity = 9.81
        self.color_terrain = "dark green"

        # setup sprite terrain
        self.position = Vector2(1000, 1000)
        self.size = Vector2(5000, WINDOW_HEIGHT/4)

        self.image = Surface(self.size)
        self.rect = Rect(self.position, self.size)
        self.image.fill(self.color_terrain)

    

class YSortCameraGroup(sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = Vector2()

        self.zoom_factor = 1


    def custom_draw(self, rocket, world):
        # calculate offset
        self.calculate_offset(rocket)

        # draw terrain
        world.render(self.display_surface, self.offset, self.zoom_factor)

        # draw rocket
        rocket.render(self.display_surface, self.offset, self.zoom_factor)


    def calculate_offset(self, rocket):
        self.offset.x = rocket.rect.centerx - self.half_width / self.zoom_factor
        self.offset.y = rocket.rect.centery - self.half_height / self.zoom_factor