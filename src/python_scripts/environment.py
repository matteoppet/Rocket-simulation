from pygame import sprite, transform, Surface
from math import exp


class Terrain(sprite.Sprite):
    def __init__(self, id, size, pos, color, group):
        sprite.Sprite.__init__(self)
        super().__init__(group)

        self.id = id

        self.image = Surface(size)
        self.rect = self.image.get_rect(topleft=pos)
        self.image.fill(color)      


class Environment:
    def __init__(self, name, gravity, drag_coeff, air_density_sea_level, beginning_of_space):
        self.name = name 
        self.gravity = gravity
        self.drag_coeff = drag_coeff
        self.air_density_sea_level = air_density_sea_level
        self.beginning_of_space = beginning_of_space
        self.scale_height = 7000
 

    def update_forces(self, rocket_altitude):
        # update gravity
        current_gravity = self.gravity * float((6371000 / (6371000 + rocket_altitude)) ** 2)

        # update air density
        current_air_density = self.air_density_sea_level * exp(-rocket_altitude/self.scale_height)

        return current_gravity, current_air_density


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
