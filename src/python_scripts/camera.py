import pygame

class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.Vector2()

        self.zoom_factor = 1
        
        self.font = pygame.font.SysFont("Calibri", 18)
        self.color_text = "white"


    def render_simulation(self, rocket, world):
        self.calculate_offset_display(rocket)
        self.display_surface.fill("#1e2629")

        world.update_position_terrains(rocket)
        world.render_terrain(self.display_surface, self.offset, self.zoom_factor)

        rocket.render(self.display_surface, self.offset, self.zoom_factor)

        self.render_UI(rocket)


    def render_planets(self):
        self.display_surface.fill("purple")


    def calculate_offset_display(self, rocket):
        self.offset.x = rocket.rect.centerx - self.half_width / self.zoom_factor
        self.offset.y = rocket.rect.centery - self.half_height / self.zoom_factor


    def render_UI(self, rocket):
        rect_background = pygame.Rect(10, 10, 190, 240)
        pygame.draw.rect(self.display_surface, "#31373a", rect_background, border_radius=3)

        text_acceleration = self.font.render(f"Acceleration: ({round(rocket.horizontal_acc.value, 1)}, {round(rocket.vertical_acc.value,1)})", False, self.color_text)
        text_velocity = self.font.render(f"Velocity: ({round(rocket.horizontal_vel.value,1)}, {round(rocket.vertical_vel.value,1)})", False, self.color_text)
        text_angular_acc = self.font.render(f"Angular acc: {round(rocket.angular_acc.value,1)}", False, self.color_text)
        text_angular_vel = self.font.render(f"Angular vel: {round(rocket.angular_vel.value,1)}", False, self.color_text)
        text_angle = self.font.render(f"Angle: {round(rocket.angle)}", False, self.color_text)
        text_altitude = self.font.render(f"Altitude: {rocket.get_altitude}", False, self.color_text)
        text_thrust_percentage = self.font.render(f"Main thrust: {rocket.main_thrust_percentage}", False, self.color_text)
        text_fuel = self.font.render(f"Fuel: {round(rocket.get_fuel_remaining)}", False, self.color_text)
        text_mass = self.font.render(f"Mass: {round(rocket.current_mass)}", False, self.color_text)
        text_speed = self.font.render(f"speed: {round(rocket.speed)}m/s", False, self.color_text)
        text_TWR = self.font.render(f"TWR: {round(rocket.get_thrust_to_weight_ratio, 1)}", False, self.color_text)

        y_pos = rect_background.y + 10
        x_pos = rect_background.x + 10
        self.display_surface.blit(text_acceleration, (x_pos, y_pos))
        self.display_surface.blit(text_velocity, (x_pos, y_pos+20))
        self.display_surface.blit(text_angular_acc, (x_pos, y_pos+40))
        self.display_surface.blit(text_angular_vel, (x_pos, y_pos+60))
        self.display_surface.blit(text_angle, (x_pos, y_pos+80))
        self.display_surface.blit(text_altitude, (x_pos, y_pos+100))
        self.display_surface.blit(text_thrust_percentage, (x_pos, y_pos+120))
        self.display_surface.blit(text_fuel, (x_pos, y_pos+140))
        self.display_surface.blit(text_mass, (x_pos, y_pos+160))
        self.display_surface.blit(text_speed, (x_pos, y_pos+180))
        self.display_surface.blit(text_TWR, (x_pos, y_pos+200))


    def increase_decrease_zoom(self, type):
        if type == "decrease":
            if self.zoom_factor > 0:
                self.zoom_factor -= 0.1
        if type == "increase":
            if self.zoom_factor < 6:
                self.zoom_factor += 1