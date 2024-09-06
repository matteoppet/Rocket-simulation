from pygame import sprite, Rect, Surface, Vector2, display, transform, draw, font
from python_scripts.settings import *


class Terrain(sprite.Sprite):
    def __init__(self, id, size, pos, color, group):
        sprite.Sprite.__init__(self)
        super().__init__(group)

        self.id = id

        self.image = Surface(size)
        self.rect = self.image.get_rect(topleft=pos)
        self.image.fill(color)



class General_world():
    def init_stack_terrain(self):
        """ Create the stack terrain group and init the first three terrain blocks
        """
        self.stack_terrain = sprite.Group()

        position = self.starting_position

        for i in range(3):
            terrain = Terrain(i, self.size, position, self.color, self.stack_terrain)
            position = (terrain.rect.bottomright[0], position[1])


    def render_terrain(self, screen, offset, zoom_factor):
        # calculate offset
        for terrain in self.stack_terrain:
            image_offset, position_offset = self.calculate_offset_terrain(offset, zoom_factor, terrain)
            screen.blit(image_offset, position_offset)


    def calculate_offset_terrain(self, offset, zoom_factor, current_terrain):
        """Calculates the offset for each stack's rectangle

        Args:
            offset (Vector2): offset position window
            zoom_factor (int): zoom of the camera
            current_terrain (Sprite): Current rectangle updated

        Returns:
            tuple int: return new image and new position of the rectangle
        """
        new_position = (current_terrain.rect.topleft - offset) * zoom_factor
        new_image = transform.scale(
            current_terrain.image,
            (int(current_terrain.image.get_width() * zoom_factor), int(current_terrain.image.get_height() * zoom_factor))
        )

        return new_image, new_position
    
    
    def update_position_terrains(self, rocket):
        """Updates the position of each rectangle based on the rocket's position

        Args:
            rocket (Sprite object): Class of the rocket with the variable position
        """

        # right
        if rocket.position.x > self.stack_terrain.sprites()[1].rect.centerx:
            self.stack_terrain.sprites()[0].kill()

            for sprite in self.stack_terrain.sprites():
                sprite.id -= 1

            Terrain(2, self.size, self.stack_terrain.sprites()[1].rect.topright, self.color, self.stack_terrain)

        # left
        self.count -= 1
        if self.count < 0: self.count = 0

        if rocket.rect.centerx < self.stack_terrain.sprites()[self.count].rect.centerx:
            self.stack_terrain.sprites()[0].kill()

            for sprite in self.stack_terrain.sprites():
                sprite.id -= 1

            # position
            x = self.stack_terrain.sprites()[0].rect.topleft[0] - self.stack_terrain.sprites()[0].image.get_size()[0]
            y = self.stack_terrain.sprites()[0].rect.topleft[1]
            Terrain(2, self.size, (x,y), self.color, self.stack_terrain)

            # TODO: check later, problem in github #21


class Earth(General_world):
    def __init__(self, window_size):
        super().__init__()

        # ! ATTRIBUTES WORLD
        self.name = "earth"
        self.drag_coeff = 0.1
        self.gravity = 9.81

        # ! TERRAIN CHARACTERISTIC
        self.starting_position = (0,80)
        #self.size = (window_size[0], window_size[1]/2)
        self.size = (100, 100)
        self.color = "dark green"

        self.count = 2
        self.init_stack_terrain()


class YSortCameraGroup(sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = Vector2()

        self.zoom_factor = 1


    def custom_draw(self, rocket, world):
        self.display_surface.fill(BACKGROUND_COLOR)

        # calculate offset
        self.calculate_offset(rocket)

        # draw terrain
        world.update_position_terrains(rocket)
        world.render_terrain(self.display_surface, self.offset, self.zoom_factor)

        # draw rocket
        rocket.render(self.display_surface, self.offset, self.zoom_factor)


    def calculate_offset(self, rocket):
        self.offset.x = rocket.rect.centerx - self.half_width / self.zoom_factor
        self.offset.y = rocket.rect.centery - self.half_height / self.zoom_factor


    def increase_decrease_zoom(self, type):
        if type == "increase":
            if self.zoom_factor != 6:
                self.zoom_factor += 1
        if type == "decrease":
            if self.zoom_factor != 1:
                self.zoom_factor -= 1