import pygame
import math
import time

class RocketCalculation:
    def __init__(self, rocket_settings: dict, engine_settings: dict, environment_settings: dict, mission_settings: dict, launch_platform_position: tuple, size_object: tuple):
        self.rocket_settings = rocket_settings
        self.engine_settings = engine_settings
        self.environment_settings = environment_settings
        self.mission_settings = mission_settings
        self.launch_platform_position = launch_platform_position
        self.size_object = size_object

        self.current_stage = 1

        self.set_constants()
        self.reset_variables()


    def set_constants(self) -> None:
        self.size = pygame.Vector2(self.size_object)
        self.dry_mass = self.rocket_settings[self.current_stage]["dry mass"]["value"]
        self.fuel_mass = self.rocket_settings[self.current_stage]["propellant mass"]["value"]

        self.max_thrust_power = self.engine_settings[self.current_stage]["thrust power"]["value"]
        self.max_gimbal_angle = self.engine_settings[self.current_stage]["thrust vector angle"]["value"]
        self.isp_engine = self.engine_settings[self.current_stage]["ISP"]["value"]

        self.drag_coeff = self.rocket_settings[self.current_stage]["cd"]["value"]
        self.air_density = self.environment_settings["air density"]["value"]
        self.gravity = self.environment_settings["gravity"]["value"]

        self.launch_rocket_angle = self.mission_settings["initial flight angle"]["value"]
        
        self.total_num_stages = len(self.rocket_settings.keys())

        self.wind_speed = self.environment_settings["wind velocity"]["value"]
        self.wind_angle = 45
        self.wind_velocity = pygame.Vector2(
            self.wind_speed * math.cos(math.radians(self.wind_angle)),
            self.wind_speed * math.sin(math.radians(self.wind_angle))
        )


    def reset_variables(self) -> None:
        self.position = pygame.Vector2(self.launch_platform_position[0], self.launch_platform_position[1]-self.size.y/2)

        self.altitude = 0
        self.apogee = 0

        self.acceleration = pygame.Vector2()
        self.velocity = pygame.Vector2()
        self.angular_acceleration = 0
        self.angular_velocity = 0
        self.thrust_vector = pygame.Vector2()
        self.gimbal_angle = 0
        self.rocket_angle = self.launch_rocket_angle
        
        self.current_mass = self.dry_mass + self.fuel_mass
        self.current_fuel = self.fuel_mass
        self.current_thrust_power = 0
        self.current_thrust_percentage = 0

        self.time_thrust_burning = 0
        self.start_time = None
    

    def update_velocity(self, dt: int) -> None:
        # * formula: resultance force / mass
        self.acceleration = self.get_resultance_force_from_thrust/self.current_mass
        # * formula: euler integration
        self.velocity += self.acceleration * dt


    def update_angular_velocity(self, dt: int) -> None:
        # * formula: torque / inertia
        self.angular_acceleration = self.get_total_torque_acting_on_object / self.get_inertia
        self.angular_velocity += self.angular_acceleration * dt


    def update_mass_fuel_rate(self) -> None:
        fuel_burnt = self.get_mass_flow_rate * int(self.time_thrust_burning)

        if self.current_fuel <= 0:
            self.current_fuel = 0
            self.current_thrust_percentage = 0
            self.current_thrust_power = 0
        else:
            self.current_mass -= fuel_burnt
            self.current_fuel -= fuel_burnt


    def update_drag(self) -> pygame.Vector2: # * formula: 1/2 * p * v**2 * Cd * A
        relative_velocity = self.get_relative_velocity
        if relative_velocity.length() == 0:
            return pygame.Vector2(0,0)

        drag_magnitude = 0.5 * self.get_air_density * (relative_velocity.length()**2) * self.drag_coeff * self.get_cross_sectional_area
        drag_direction = relative_velocity.normalize()
        drag_vector = drag_direction * drag_magnitude
        return drag_vector      


    @property
    def get_relative_velocity(self) -> pygame.Vector2:
        return self.velocity - self.wind_velocity
    @property
    def get_air_density(self) -> float:
        return self.air_density * (1-(self.get_altitude/100000)*2)
    @property
    def get_altitude(self) -> int:
        return self.launch_platform_position[1] - self.position.y
    @property
    def get_center_of_mass(self) -> pygame.Vector2:
        return pygame.Vector2(self.size.x/2, self.size.y/2)
    @property
    def get_inertia(self) -> float:
        return (1/12) * self.current_mass * (3 * (self.size.x/2)**2 + (self.size.y**2))
    @property
    def get_cross_sectional_area(self) -> float:
        angle_in_radians = math.radians(self.rocket_angle)
        return abs(self.size.x*math.cos(angle_in_radians)) + abs(self.size.y*math.sin(angle_in_radians))
    @property
    def get_mass_flow_rate(self) -> float:
        return self.current_thrust_power/(self.isp_engine*self.gravity)
    
    def calculate_lever_arm(self, position_force_applied: pygame.Vector2) -> pygame.Vector2:
        return position_force_applied - self.get_center_of_mass



    @property
    def get_lever_arm_horizontal_wind(self) -> float:
        return (self.size.y/2) * math.sin(self.get_angle_of_attack_wind)
    @property
    def get_lever_arm_vertical_wind(self) -> float:
        return (self.size.x/2) * math.cos(self.get_angle_of_attack_wind)
    @property
    def get_torque_from_wind(self) -> float:
        torque_horizontal = self.get_lever_arm_horizontal_wind * self.update_drag().length()
        torque_vertical = self.get_lever_arm_vertical_wind * self.update_drag().length()
        return torque_horizontal + torque_vertical
    @property
    def get_total_torque_acting_on_object(self) -> float:
        return self.get_torque_from_thrust + self.get_torque_from_wind
    @property
    def get_angle_of_attack_wind(self) -> float:
        angle = self.wind_angle - self.rocket_angle
        return math.radians(angle)


    @property
    def get_force_generated_by_drag(self) -> float:
        return 0.5 * self.get_air_density * (self.get_relative_velocity.length()**2) * self.drag_coeff * self.get_cross_sectional_area
    @property
    def get_total_weight(self) -> pygame.Vector2:
        return pygame.Vector2(0, self.current_mass*self.gravity)
    @property
    def get_resultance_force_from_thrust(self) -> pygame.Vector2:
        return self.thrust_vector - self.get_total_weight - self.update_drag()
    @property
    def get_current_thrust_power(self) -> float:
        return (self.current_thrust_percentage/100)*self.max_thrust_power
    @property
    def get_total_thrust_angle(self) -> int:
        return self.rocket_angle + self.gimbal_angle
    @property
    def get_thrust_to_weight_ratio(self) -> float:
        return self.current_thrust_power / (self.current_mass * self.gravity)
    @property
    def get_torque_from_thrust(self) -> float:
        position_thrust = pygame.Vector2(self.size.x/2, self.size.y)
        lever_arm = self.calculate_lever_arm(position_thrust)
        return self.current_thrust_power * lever_arm.length() * math.sin(math.radians(self.gimbal_angle))
    @property
    def get_splitted_thrust(self) -> float:
        total_thrust_angle_radians = math.radians(self.get_total_thrust_angle)
        thrust_x = self.current_thrust_power * math.sin(total_thrust_angle_radians)
        thrust_y = self.current_thrust_power * math.cos(total_thrust_angle_radians)
        return thrust_x, thrust_y


class Rocket(pygame.sprite.Sprite, RocketCalculation):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        path_image = '../assets/images/prototype.png'
        self.image = pygame.image.load(path_image).convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(0,0))    

        self.direction = pygame.Vector2()

    def initialize_calculation_class(self, rocket_settings: dict, engine_settings: dict, environment_settings: dict, mission_settings: dict, launch_platform: tuple) -> None:
        RocketCalculation.__init__(self, rocket_settings, engine_settings, environment_settings, mission_settings, launch_platform, self.image.get_size())

    def render(self, screen: pygame.Surface, offset: bool=None) -> None:
        if offset is not None:
            rocket_pos = self.rect.topleft - offset
        else:
            rocket_pos = self.rect.topleft

        rotated_image = pygame.transform.rotate(self.copy_image, self.rocket_angle)
        screen.blit(rotated_image, rocket_pos)

    def run(self, dt: int) -> None:
        self.current_thrust_power = self.get_current_thrust_power

        if self.rocket_angle < 0: self.rocket_angle = 360
        elif self.rocket_angle > 360: self.rocket_angle = 0

        if self.current_thrust_power <= 0: self.start_time = None
        if self.start_time is not None: self.time_thrust_burning = time.time() - self.start_time
        else: self.time_thrust_burning = 0

        if self.get_altitude > self.apogee: self.apogee = self.get_altitude

        self.run_calculation_functions(dt)
        self.update_position(dt)

    
    def run_calculation_functions(self, dt: int) -> None:
        self.thrust_vector = pygame.Vector2(self.get_splitted_thrust)
        
        self.update_mass_fuel_rate()
        self.update_velocity(dt)
        self.update_angular_velocity(dt)


    def update_position(self, dt: int) -> None:
        angular_velocity_deg = self.angular_acceleration * (180 / math.pi)
        self.rocket_angle += angular_velocity_deg * dt
        self.position -= self.velocity
        self.rect.center = self.position
        self.direction.y = self.velocity.y


    def collision(self, group_rect: list) -> None:
        if self.direction.magnitude() != 0: self.direction = self.direction.normalize()

        for sprite in group_rect:
            if sprite.rect.colliderect(self.rect):
                if self.direction.y < 0:
                    self.rect.bottom = sprite.rect.top
                    self.position.y = self.rect.bottom - self.size.y/2
                    self.velocity = pygame.Vector2()


    def controls(self) -> None:
        keys = pygame.key.get_pressed()

        # control power engine
        if keys[pygame.K_w]:
            if self.current_thrust_percentage < 100 and self.current_fuel > 0:
                self.current_thrust_percentage += 10
                self.start_time = time.time()
        elif keys[pygame.K_s]:
            if self.current_thrust_percentage > 0: self.current_thrust_percentage
            else: self.start_time = None
        elif keys[pygame.K_x]:
            if self.current_fuel > 0:
                self.current_thrust_percentage = 100
                self.start_time = time.time()
        elif keys[pygame.K_z]:
            self.current_thrust_percentage = 0
            self.start_time = None

        # move gimbal thrust
        if keys[pygame.K_d]:
            if self.gimbal_angle < self.max_gimbal_angle: self.gimbal_angle += 1
        elif keys[pygame.K_a]:
            if self.gimbal_angle > -self.max_gimbal_angle: self.gimbal_angle -= 1
        else: self.gimbal_angle = 0
            