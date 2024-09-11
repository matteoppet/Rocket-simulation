import pygame

class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.Vector2()

        self.zoom_factor = 1


    def render_simulation(self, rocket, world):
        self.calculate_offset_display(rocket)
        self.display_surface.fill("black")

        world.update_position_terrains(rocket)
        world.render_terrain(self.display_surface, self.offset, self.zoom_factor)

        rocket.render(self.display_surface, self.offset, self.zoom_factor)


    def render_planets(self):
        self.display_surface.fill("purple")


    def calculate_offset_display(self, rocket):
        self.offset.x = rocket.rect.centerx - self.half_width / self.zoom_factor
        self.offset.y = rocket.rect.centery - self.half_height / self.zoom_factor