import pygame
from python_scripts.camera import Camera
from python_scripts.rocket import Rocket
from python_scripts.planets import Earth
from settings import *


class Button(pygame.sprite.Sprite):
    def __init__(self, image, position, type, to_go, group):
        super().__init__(group)

        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.image.fill("white")

        self.type = type
        self.to_go = to_go


class Simulation:
    def __init__(self):
        self.clock = pygame.time.Clock()

        self.CURRENT_PLANET = "earth"
        self.CURRENT_SCREEN = "simulation"

        self.visible_sprites = Camera()
        self.world_sprites = pygame.sprite.Group()
        self.button_sprites = pygame.sprite.Group()
        self.dict_button_for_each_screen = {
            "simulation": [],
            "planets": [],
        }

        self.ROCKET = Rocket(self.visible_sprites)
        self.EARTH = Earth((WINDOW_WIDTH, WINDOW_HEIGHT), self.world_sprites)


    def run(self):
        while True:
            self.event_handling()
            self.screen_handling()
            
            # create or draw
            if len(self.button_sprites) == 0:
                self.create_buttons()
            else:
                for button in self.button_sprites.sprites():
                    self.visible_sprites.display_surface.blit(button.image, button.rect)

            pygame.display.flip()
            self.clock.tick(60)


    def event_handling(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
            
            if event.type == pygame.MOUSEWHEEL:
                if event.y >= 1:
                    self.visible_sprites.increase_decrease_zoom("increase")
                if event.y <= -1:
                    self.visible_sprites.increase_decrease_zoom("decrease")

            # handle button click
            if len(self.button_sprites.sprites()) != 0:
                for button in self.button_sprites.sprites():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            if button.type == "change screen":
                                self.CURRENT_SCREEN = button.to_go
                                self.button_sprites.empty()


    def screen_handling(self):
        if self.CURRENT_SCREEN == "simulation":
            for world in self.world_sprites:
                if world.name == self.CURRENT_PLANET:
                    self.visible_sprites.render_simulation(self.ROCKET, world)

                    dt = self.clock.tick(60)/1000.0
                    self.ROCKET.controls()
                    self.ROCKET.current_state(world, dt)

                    self.ROCKET.collision(world.stack_terrain)

        elif self.CURRENT_SCREEN == "planets":
            self.visible_sprites.render_planets()


    def create_buttons(self):
        if self.CURRENT_SCREEN == "simulation":
            self.dict_button_for_each_screen["simulation"].append(
                Button(pygame.Surface((20,20)), (WINDOW_WIDTH-40, 30), "change screen", "planets", self.button_sprites)
            )

        if self.CURRENT_SCREEN == "planets":
            self.dict_button_for_each_screen["planets"].append(
                Button(pygame.Surface((20,20)), (WINDOW_WIDTH-40, 30), "change screen", "simulation", self.button_sprites)
            )