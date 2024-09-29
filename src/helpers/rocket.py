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
        return self.get_current_thrust_power * 40 * math.sin(self.gimbal_angle)
    
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
        return 1

    @property
    def get_mass_flow_rate(self):
        return self.get_current_thrust_power/(self.isp * self.gravity)
    
    @property
    def get_current_thrust_power(self):
        return (self.current_thrust_percentage/100)*self.max_thrust_power

    
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
        self.angular_acceration = self.get_torque / self.get_inertia

    def calculate_angular_velocity(self, dt):
        self.angular_velocity = self.angular_acceration * dt 
    
    def calculate_drag(self):
        # formula: 1/2 * p * v**2 * Cd * A
        drag_magnitude = 0.5 * self.get_air_density * (self.velocity.length()**2) * self.drag_coeff * self.get_cross_sectional_area
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
    def __init__(self):
        self.size = pygame.Vector2(10, 80)
        self.temp_start_pos = pygame.Vector2(200, 930)

        # Rocket
        self.image = pygame.image.load("../assets/images/prototype.png").convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.temp_start_pos.x, self.temp_start_pos.y))

        # Thrust = gimbaled
        self.image_thrust = pygame.image.load("../assets/images/thrust.png").convert_alpha()
        self.copy_image_thrust = self.image_thrust.copy()


    def set_parameters(self, parameters_dict):
        self.gravity = parameters_dict["environmental-settings"]["variables"]["gravity"]["value"]
        self.air_density_sea_level = parameters_dict["environmental-settings"]["variables"]["air-density-sea-level"]["value"]

        self.drag_coeff = parameters_dict["rocket-specific-settings"]["variables"]["cd"]["value"]
        self.initial_dry_mass = parameters_dict["rocket-specific-settings"]["variables"]["dry-mass"]["value"]
        self.initial_fuel_mass = parameters_dict["rocket-specific-settings"]["variables"]["fuel-mass"]["value"]

        self.isp = parameters_dict["engine-settings"]["variables"]["isp"]["value"]
        self.max_thrust_power = parameters_dict["engine-settings"]["variables"]["power"]["value"]
        self.thrust_vectoring = parameters_dict["engine-settings"]["variables"]["thrust_vectoring"]["value"]

        self.initial_rocket_angle = parameters_dict["mission-specific-parameters"]["variables"]["start-angle"]["value"]
        self.initial_altitude = parameters_dict["mission-specific-parameters"]["variables"]["start-altitude"]["value"]

    def reset(self):
        self.position = pygame.Vector2(self.temp_start_pos.x, self.initial_altitude)
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

    def collision(self, rect):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

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

    def run(self, dt):
        self.current_thrust_power = self.get_current_thrust_power
        
        if self.get_weight.y > self.max_thrust_power:
            print("ERROR: Thrust power too lower for the weight of the rocket")

        self.calculate_mass_fuel_consumption()
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)

        self.calculate_acceleration()
        self.calculate_velocity(dt)
        self.calculate_angular_acceleration()
        self.calculate_angular_velocity(dt)
        self.calculate_drag()

        # update position and direction rocket
        angular_velocity_deg = self.angular_acceleration * (180 / math.pi)
        self.rocket_angle += angular_velocity_deg * dt
        self.position -= self.velocity
        self.rect.center = self.position
        self.direction.y = self.velocity.y