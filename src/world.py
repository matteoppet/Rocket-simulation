from pygame import sprite, Rect, Surface, Vector2, display, transform
from settings import *

class Terrain(sprite.Sprite):
    def __init__(self, window_width, window_height, group):
        super().__init__(group)
        sprite.Sprite.__init__(self)
                                    
        self.size = (window_width, window_height/4)
        self.position = Vector2(0, window_height-self.size[1])
        self.color = "dark green"

        self.image = Surface(self.size)
        self.rect = Rect(self.position, self.size)
        self.image.fill(self.color)


    def collisions(self, sprite_1, sprite_2):
        if sprite_1.rect.colliderect(sprite_2):
            if not sprite_1.on_platform:
                sprite_1.collision = True
                sprite_1.reset()

    def draw(self, screen, offset, zoom_factor):
        offset_rect = (self.rect.topleft - offset) * zoom_factor
        screen.blit(self.image, self.rect)



class YSortCameraGroup(sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = Vector2()

        self.zoom_factor = 1


    def custom_draw(self, rocket, terrain):
        self.offset.x = rocket.rect.centerx - self.half_width / self.zoom_factor
        self.offset.y = rocket.rect.centery - self.half_height / self.zoom_factor

        # draw terrain
        # terrain.draw(self.display_surface, self.offset, self.zoom_factor)
        terrain_offset_position = (terrain.rect.topleft - self.offset) * self.zoom_factor
        terrain_scaled_image = transform.scale(
            terrain.image,
            (int(terrain.image.get_width() * self.zoom_factor),
             int(terrain.image.get_height() * self.zoom_factor)))
        self.display_surface.blit(terrain_scaled_image, terrain_offset_position)

        # draw rocket
        rocket_offset_pos = (rocket.rect.topleft - self.offset) * self.zoom_factor
        rocket_scaled_image = transform.scale(
            rocket.image,
            (int(rocket.image.get_width() * self.zoom_factor),
             int(rocket.image.get_height() * self.zoom_factor)))
        rocket_scaled_image = transform.rotate(rocket_scaled_image, rocket.angle)
        self.display_surface.blit(rocket_scaled_image, rocket_offset_pos)