import pygame
import time
import numpy as np


class RocketCalculation:
    current_stage = 1

    def set_constants(self, rocket_settings: dict, engine_settings: dict, environment_settings: dict, mission_settings: dict, launch_platform: pygame.Rect) -> None:
        self.rocket_settings = rocket_settings
        self.engine_settings = engine_settings
        self.environment_settings = environment_settings
        self.mission_settings = mission_settings
        self.launch_platform = launch_platform
        
        self.size = pygame.Vector2(22, 160)
        self.thrust_position = np.array([0, self.size.y/2])
        self.center_of_mass = np.array([0,0])

        self.center_of_pressure = np.array([self.center_of_mass[0], self.center_of_mass[1]+40]) # CoP at 0 AoA
        self.center_of_pressure_sensitivity = 1.0
        self.center_of_pressure_max = self.size.y/2
        self.center_of_pressure_min = -self.size.y/2

        self.wind_speed = self.environment_settings["wind velocity"]
        self.wind_angle = 45
        self.wind_velocity = np.array([
            self.wind_speed * np.sin(np.radians(self.wind_angle)),
            self.wind_speed * np.cos(np.radians(self.wind_angle)),
        ])

        self.air_density = self.environment_settings["air density"]
        self.drag_coeff = self.rocket_settings[self.current_stage]["cd"]
        self.gravity = self.environment_settings["gravity"]

        self.dry_mass = self.rocket_settings[self.current_stage]["dry mass"]
        self.fuel_mass = self.rocket_settings[self.current_stage]["propellant mass"]

        self.max_force_thrust = self.engine_settings[self.current_stage]["thrust power"]
        self.max_thrust_angle = self.engine_settings[self.current_stage]["thrust vector angle"]
        self.isp_engine = self.engine_settings[self.current_stage]["isp"]

    def set_variables(self) -> None:
        self.rocket_angle = 0
        self.thrust_angle = 0

        self.force_thrust = 0
        self.force_thrust_percentage = 0
        self.time_thrust_burning = 0

        self.acceleration = np.array([0.0,0.0])
        self.velocity = np.array([0.0,0.0])
        self.wind_speed = 5
        self.wind_angle = 180
        self.angular_acceration = 0
        self.angular_velocity = 0

        self.position = np.array([self.launch_platform.centerx-self.size.x/2,self.launch_platform.centery-self.size.y])
        self.apogee = 0

        self.test = 0


    def update_state(self, dt) -> None:
        """ How each state works
        acceleration -> velocity -> position -> render rocket
        gimbal thrust -> torque -> angular acceleration -> angular velocity

        acceleration = net force / mass
        upwards forces = thrust
        opposing forces = gravity, mass rocket, drag

        velocity wind -> center of pressure -> torque -> angular acceleration -> angular velocity
        """
        m_fuel = self.get_force_thrust / (self.isp_engine * self.gravity)
        fuel_burnt = m_fuel * self.test
        self.fuel_mass -= fuel_burnt

        # update acceleration and velocity
        net_force = self.get_thrust_vector - self.get_weight - self.get_drag
        self.acceleration = net_force / self.get_current_mass
        self.velocity += self.acceleration * dt

        # update angular acceleration and angular velocity
        self.angular_acceration = self.get_net_torque / self.get_inertia
        self.angular_velocity += self.angular_acceration * dt


    @property
    def get_relative_wind_aoa(self):
        relative_aoa = (self.rocket_angle - self.wind_angle) % 360
        if relative_aoa > 180: relative_aoa -= 360
        return relative_aoa
    @property
    def get_current_position_cop(self):
        angle = self.get_relative_wind_aoa
        if angle < 0: new = max(-70, self.center_of_pressure[1]-abs(angle))
        elif angle >= 0: new = max(-70, (self.center_of_pressure[1]-angle))
        return (self.center_of_pressure[0], new)
    @property
    def get_relative_velocity(self):
        wind_velocity_vector = np.array([
            self.wind_speed * np.cos(np.radians(self.wind_angle)),
            self.wind_speed * np.sin(np.radians(self.wind_angle))
        ])
        return self.velocity - wind_velocity_vector
    @property
    def get_thrust_vector(self):
        angle_radians = np.radians(self.rocket_angle)
        thrust_x = self.get_force_thrust * np.sin(angle_radians)
        thrust_y = self.get_force_thrust * np.cos(angle_radians)
        return np.array([thrust_x, thrust_y])
    @property 
    def get_inertia(self):
        return (1/12) * self.get_current_mass * (3 * np.power(self.size.x/2, 2) + np.power(self.size.y, 2))
    @property
    def get_torque_thrust(self):
        thrust_vector = np.array([
            self.get_force_thrust * np.sin(np.radians(self.thrust_angle)),
            self.get_force_thrust * np.cos(np.radians(self.thrust_angle))
        ])
        lever_arm_vector = self.center_of_mass - self.thrust_position
        return np.cross(lever_arm_vector, thrust_vector)
    @property
    def get_torque_wind(self):
        lever_arm = self.center_of_mass - self.get_current_position_cop
        wind_vector = self.get_drag
        return np.cross(lever_arm, wind_vector)
    @property
    def get_net_torque(self):
        return self.get_torque_thrust + self.get_torque_wind
    @property
    def get_cross_sectional_area(self):
        if self.rocket_angle == 0 or self.rocket_angle == 180:
            return np.pi*((self.size.x/2)**2)
        if self.rocket_angle == 90 or self.rocket_angle == 270:
            return self.size.x*self.size.y
        else:
            angle_in_radians = np.radians(self.rocket_angle)
            return (self.size.x * abs(np.sin(angle_in_radians))) + (self.size.y * abs(np.cos(angle_in_radians)))
    @property
    def get_drag(self):
        speed = np.linalg.norm(self.get_relative_velocity)
        drag_magnitude = 0.5 * self.drag_coeff * self.get_cross_sectional_area * self.air_density * (speed**2)
        drag_direction = self.velocity / speed if speed > 0 else np.array([0.0, 0.0])
        drag = drag_direction * drag_magnitude
        return drag
    @property
    def get_current_mass(self):
        return self.dry_mass + self.fuel_mass
    @property
    def get_weight(self):
        return np.array([0, self.get_current_mass*self.gravity])
    @property
    def get_force_thrust(self):
        return (self.force_thrust_percentage/100)*self.max_force_thrust
    @property
    def get_altitude(self):
        return self.launch_platform.y - self.position[1]



class Rocket(RocketCalculation, pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        super().__init__()

        path_image = '../assets/images/prototype_rockets/test_rocket_small.png'
        self.image = pygame.image.load(path_image).convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(0,0))    

        self.direction = pygame.Vector2()

    def render(self, screen: pygame.Surface, offset: bool=None) -> None:
        scaled_image = pygame.transform.smoothscale(self.copy_image, (22, 160))
        rotated_image = pygame.transform.rotate(scaled_image, self.rocket_angle)
        self.rect = rotated_image.get_rect(center=self.position)

        if offset is not None: position = self.rect.topleft - offset
        else: position = self.rect

        screen.blit(rotated_image, position)

        center_circle_cop = self.position + self.get_current_position_cop
        pygame.draw.circle(screen, "red", center_circle_cop, 5)
        center_circle_com = self.position + self.center_of_mass
        pygame.draw.circle(screen, "blue", center_circle_com, 5)
        center_circle_pos = self.position
        pygame.draw.circle(screen, "green", center_circle_pos, 5)

        center_circle_wind_blowing = (
            self.position[0]+100 * np.sin(np.radians(self.get_relative_wind_aoa)),
            self.position[1]+100 * np.cos(np.radians(self.get_relative_wind_aoa))
        )
        pygame.draw.circle(screen, "purple", center_circle_wind_blowing, 5)


    def run(self, dt: int) -> None:
        self.force_thrust = self.get_force_thrust
        self.rocket_angle = self.rocket_angle % 360

        if self.rocket_angle < 0: self.rocket_angle = 360
        elif self.rocket_angle > 360: self.rocket_angle = 0

        if self.get_force_thrust > 0: self.time_thrust_burning += dt
        else: self.time_thrust_burning = 0

        self.update_state(dt)
        self.update_position(dt)

    def update_position(self, dt: int) -> None:
        angular_velocity_deg = self.angular_acceration * (180 / np.pi)
        self.rocket_angle += angular_velocity_deg * dt

        self.position[0] -= float(self.velocity[0])
        self.position[1] -= float(self.velocity[1])
        
        self.rect.center = self.position
        self.direction.y = self.velocity[1]


    def collision(self, group_rect: list) -> None:
        if self.direction.magnitude() != 0: self.direction = self.direction.normalize()

        for sprite in group_rect:
            if sprite.rect.colliderect(self.rect):
                if self.direction.y < 0:
                    self.rect.bottom = sprite.rect.top
                    self.position[0] = self.rect.centerx
                    self.position[1] = self.rect.centery
                    self.velocity = np.array([0.0, 0.0])


    def controls(self) -> None:
        keys = pygame.key.get_pressed()

        # control power engine
        if keys[pygame.K_w]:
            if self.force_thrust_percentage < 100 and self.fuel_mass > 0: self.force_thrust_percentage += 1
        elif keys[pygame.K_s]:
            if self.force_thrust_percentage > 0: self.force_thrust_percentage -= 1
        elif keys[pygame.K_x]:
            if self.fuel_mass > 0: self.force_thrust_percentage = 100
        elif keys[pygame.K_z]: self.force_thrust_percentage = 0

        if keys[pygame.K_l]: self.wind_angle += 1
        elif keys[pygame.K_k]: self.wind_angle -= 1

        if keys[pygame.K_p]: self.center_of_mass[1] += 1
        elif keys[pygame.K_o]: self.center_of_mass[1] -= 1

        # move gimbal thrust
        if keys[pygame.K_d]:
            if self.thrust_angle < self.max_thrust_angle: self.thrust_angle += 1
        elif keys[pygame.K_a]:
            if self.thrust_angle > -self.max_thrust_angle: self.thrust_angle -= 1
        else: self.thrust_angle = 0
            

