import pygame
from pygame.locals import *

from game.helpers.rocket import Rocket
from game.helpers.environment import Environment


class Camera:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0]//2
        self.half_height = self.display_surface.get_size()[1]//2

        self.font_UI = pygame.font.SysFont("Arial", 12)

        self.offset = pygame.Vector2()

    def render(self, ROCKET: object, ENVIRONMENT: object) -> None:
        self.offset.x = ROCKET.body.position[0] - self.half_width
        self.offset.y = ROCKET.body.position[1] - self.half_height

        # self.draw_UI(self.display_surface, ROCKET)

        ROCKET.render(self.display_surface, self.offset)
        ENVIRONMENT.render(self.display_surface, self.offset)

    def get_data_UI(self, rocket) -> list:
        variables_to_show = {
            "body": {
                "altitude": rocket.body.get_altitude,
                "angle": rocket.body.angle,
                "velocity": rocket.body.velocity,
                "angular vel": rocket.body.angular_velocity,
                "drag": rocket.body.get_drag,
                "mass": rocket.body.get_total_mass,
                "fuel mass": rocket.body.fuel_mass
            },
            "motor": {
                "angle": rocket.motor.current_angle,
                "thrust": rocket.motor.current_thrust_perc,
            },
            "environment": {
                "air density": rocket.environment.get_air_density(rocket.body.get_altitude),
                "gravity": rocket.environment.get_gravity(rocket.body.get_altitude),
                "temperature": rocket.environment.temperature,
            },
        }

        # TWR

        return variables_to_show

    def draw_UI(self, screen, rocket):
        data = self.get_data_UI(rocket)

        y_start_sections = 10
        x_start_sections = 10
        for variables in data.values():
            for variable, value in variables.items():
                text = self.font_UI.render(f"{variable}: {value}", True, "black")
                screen.blit(text, (x_start_sections, y_start_sections))
                y_start_sections += 15
            
            y_start_sections += 20

class Simulation:
    def __init__(self):
        self.track = False
        self.WINDOW_SIZE = (1800, 1000)

        self.FLAGS = DOUBLEBUF
        self.screen = None
        
    def run(self, launch_pad_settings):
        pygame.init()
        
        if not self.screen:
            self.screen = pygame.display.set_mode(self.WINDOW_SIZE, self.FLAGS)
            self.clock = pygame.time.Clock()
            pygame.font.init()
            pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

            self.ENVIRONMENT = Environment(self.WINDOW_SIZE)
            self.ENVIRONMENT.create_environment(launch_pad_settings)
            components = {
                "nose": {
                    "local_offset": pygame.Vector2(0, 0),
                    "size": pygame.Vector2(20, 40),
                    "shape": "cone",
                    "color": "black",
                    "mass": 162.351
                },
                "tube_1": {
                    "local_offset": pygame.Vector2(0,40),
                    "size": pygame.Vector2(20, 60),
                    "shape": "cylinder",
                    "color": "yellow",
                    "mass": 1000.0
                },
                "tube_2": {
                    "local_offset": pygame.Vector2(0,60),
                    "size": pygame.Vector2(20, 80),
                    "shape": "cylinder",
                    "color": "blue",
                    "mass": 1000.0
                },
                "motor": {
                    "local_offset": pygame.Vector2(0, 140),
                    "size": pygame.Vector2(10, 20),
                    "shape": "cone",
                    "color": "black",
                    "mass": 200.0,
                    "thrust": 50000,
                    "angle_vectoring": 15,
                    "isp": 0,
                }
            }
            self.ROCKET = Rocket(components, self.ENVIRONMENT)
            self.CAMERA = Camera()
        
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        if self.track: self.track = False
                        else: self.track = True

            self.screen.fill("white")

            timestep = self.clock.tick(60)/1000.0
            self.ROCKET.update(timestep, self.ENVIRONMENT.ground_sprites)
            self.ROCKET.controls()

            if self.track: 
                self.CAMERA.render(self.ROCKET, self.ENVIRONMENT)
            else:
                self.ENVIRONMENT.render(self.screen, None)
                self.ROCKET.render(self.screen)

            pygame.display.set_caption(str(round(self.clock.get_fps(), 2)))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.display.quit()
        self.screen = None