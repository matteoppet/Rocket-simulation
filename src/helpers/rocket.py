import pygame 
from settings import *
import math


class RocketCalculation:
    @property
    def get_weight(self):
        return pygame.Vector2(0, self.current_mass * self.gravity)
    
    @property
    def get_resultance_force(self):
        return self.thrust_vector - self.get_weight - self.calculate_drag()
    
    @property
    def get_torque(self):
        return self.current_thrust_power * 40 * math.sin(math.radians(self.gimbal_angle))
    
    @property
    def get_inertia(self):
        return (1/12) * self.current_mass * ((self.size.x ** 2) + (self.size.y ** 2))
    
    @property
    def get_cross_sectional_area(self):
        angle_in_radians = math.radians(self.rocket_angle)
        return abs(self.size.x * math.cos(angle_in_radians)) + abs(self.size.y * math.sin(angle_in_radians))

    @property
    def get_air_density(self):
        return self.air_density_sea_level * (1-(self.get_altitude/100000)*2)
    
    @property
    def get_altitude(self): # TODO
        return self.base_rect_pos[1] - self.position.y

    @property
    def get_mass_flow_rate(self):
        return self.current_thrust_power/(self.isp * self.gravity)
    
    @property
    def get_current_thrust_power(self):
        return (self.current_thrust_percentage/100)*self.max_thrust_power
    
    @property
    def get_total_thrust_angle(self):
        return self.rocket_angle + self.gimbal_angle

    
    def calculate_acceleration(self):
        # formula: resultance_force/mass
        rocket_angle_radians = math.radians(self.rocket_angle)
        thrust_x = self.current_thrust_power * math.sin(rocket_angle_radians)
        thrust_y = self.current_thrust_power * math.cos(rocket_angle_radians)
        self.thrust_vector = pygame.Vector2(thrust_x, thrust_y)
        self.acceleration = self.get_resultance_force/self.current_mass

    def calculate_velocity(self, dt):
        self.velocity += self.acceleration * dt

    def calculate_angular_acceleration(self):
        # formula: torque/inertia
        self.angular_acceleration = self.get_torque / self.get_inertia

    def calculate_angular_velocity(self, dt):
        self.angular_velocity = self.angular_acceleration * dt 
    
    def calculate_drag(self):
        # formula: 1/2 * p * v**2 * Cd * A
        drag_magnitude = 0.5 * self.get_air_density * (self.velocity.magnitude()**2) * self.drag_coeff * self.get_cross_sectional_area
        if self.velocity.magnitude() != 0: drag_direction = self.velocity.normalize()
        else: drag_direction = pygame.Vector2(0, 0)
        drag_vector = drag_direction * drag_magnitude
        return drag_vector
    
    def calculate_mass_fuel_consumption(self):
        if self.current_thrust_percentage > 1:
            self.time_burn = int((pygame.time.get_ticks() - self.started_burnt)/1000)
    
        self.current_mass -= self.get_mass_flow_rate
        self.fuel_burnt = self.get_mass_flow_rate * self.time_burn

        if self.current_fuel <= 0:
            self.current_fuel = 0
            self.current_thrust_power = 0
        else:
            self.current_fuel -= self.fuel_burnt


class Rocket(pygame.sprite.Sprite, RocketCalculation):
    def __init__(self, base_rect_pos):
        self.base_rect_pos = base_rect_pos

        self.image = pygame.image.load("../assets/images/prototype.png").convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(0,0))

        self.size = pygame.Vector2(self.image.get_size())
        self.temp_start_pos = pygame.Vector2(300, base_rect_pos[1]+40-self.size.y)

        # Thrust = gimbaled
        self.image_thrust = pygame.image.load("../assets/images/thrust.png").convert_alpha()
        self.copy_image_thrust = self.image_thrust.copy()


    def set_parameters(self, rocket_settings, environment_settings, engine_settings, mission_settings):
        # do stage after
        current_stage = 1
        
        self.drag_coeff = rocket_settings[current_stage]["cd"]["value"]
        self.initial_dry_mass = rocket_settings[current_stage]["dry mass"]["value"]
        self.initial_fuel_mass = rocket_settings[current_stage]["propellant mass"]["value"]

        self.gravity = environment_settings["gravity"]["value"]
        self.air_density_sea_level = environment_settings["air density"]["value"]

        self.isp = engine_settings[current_stage]["ISP"]["value"] # TODO more engine calculation
        self.max_thrust_power = engine_settings[current_stage]["thrust power"]["value"]
        self.thrust_vectoring = engine_settings[current_stage]["thrust vector angle"]["value"]

        self.initial_altitude = mission_settings["launch altitude"]["value"]
        self.initial_rocket_angle = mission_settings["initial flight angle"]["value"]

    def reset(self, launch_platform_rect):
        self.position = pygame.Vector2(launch_platform_rect.x+launch_platform_rect.width/2, launch_platform_rect.y-self.size.y+self.size.y/2)
        self.direction = pygame.Vector2(0,0)

        self.rocket_angle = self.initial_rocket_angle
        self.current_mass = self.initial_dry_mass + self.initial_fuel_mass
        self.current_fuel = self.initial_fuel_mass
        self.max_gimbal_vectoring = self.thrust_vectoring

        self.altitude = 0
        self.acceleration = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0,0)
        self.angular_acceleration = 0
        self.angular_velocity = 0
        self.current_thrust_percentage = 0
        self.thrust_vector = pygame.Vector2(0,0)
        self.started_burnt = False
        self.time_burn = 0
        self.gimbal_angle = self.rocket_angle

    def controls(self, dt):
        keys = pygame.key.get_pressed()

        # increase decrease percentage power engine
        if keys[pygame.K_w]:
            if self.current_thrust_percentage < 100:
                self.current_thrust_percentage += 1
                self.started_burnt = pygame.time.get_ticks()
        elif keys[pygame.K_s]:
            if self.current_thrust_percentage > 0: self.current_thrust_percentage -= 1
            else: self.started_burnt = False

        # cut-on cut-off engine
        if keys[pygame.K_x]:
            if self.current_fuel > 0:
                self.current_thrust_percentage = 100
                self.started_burnt = pygame.time.get_ticks()
        elif keys[pygame.K_z]:
            self.current_thrust_percentage = 0
            self.started_burnt = False
        
        # change gimbal angle
        if keys[pygame.K_d]:
            if self.gimbal_angle < self.max_gimbal_vectoring:
                self.gimbal_angle += 1
        elif keys[pygame.K_a]:
            if self.gimbal_angle > -self.max_gimbal_vectoring:
                self.gimbal_angle -= 1
        else:
            self.gimbal_angle = 0

    def collision(self, group_rect):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        for rect in group_rect:
            if rect.colliderect(self.rect):
                if self.direction.y < 0:
                    self.rect.bottom = rect.top
                    self.position.y = self.rect.bottom-self.size.y/2
                    self.velocity = pygame.Vector2(0,0)

                if self.direction.y > 0:
                    self.rect.top = rect.bottom

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.copy_image, self.rocket_angle)
        screen.blit(rotated_image, self.rect)

        rotated_image_thrust = pygame.transform.rotate(self.copy_image_thrust, self.gimbal_angle+90)
        screen.blit(rotated_image_thrust, (self.rect.x, self.rect.y+self.size.y))

    def run(self, dt, group_rect):
        self.current_thrust_power = self.get_current_thrust_power

        self.calculate_mass_fuel_consumption()

        total_thrust_angle_radians = math.radians(self.get_total_thrust_angle)
        thrust_x = self.current_thrust_power * math.sin(total_thrust_angle_radians)
        thrust_y = self.current_thrust_power * math.cos(total_thrust_angle_radians)
        self.thrust_vector = pygame.Vector2(thrust_x, thrust_y)

        self.calculate_acceleration()
        self.calculate_velocity(dt)
        self.calculate_angular_acceleration()
        self.calculate_angular_velocity(dt)

        # update position and direction rocket
        angular_velocity_deg = self.angular_acceleration * (180 / math.pi)
        self.rocket_angle += angular_velocity_deg * dt
        self.position -= self.velocity
        self.rect.center = self.position
        self.direction.y = self.velocity.y

        self.collision(group_rect)