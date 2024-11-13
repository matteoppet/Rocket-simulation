import pygame
import numpy as np
import json

class Rocket(pygame.sprite.Sprite):
    class Body:
        def __init__(self):     
            ...

        def reset_variables(self, rocket_config, rocket_instance):
            self.rocket_instance = rocket_instance
            self.acceleration = np.array([0.0,0.0])
            self.velocity = np.array([0.0,0.0])
            self.angular_acceleration = 0
            self.angular_velocity = 0
            self.drag_coeff = 0.5

            self.angle = self.rocket_instance.environment_settings["launch angle"]
            self.wind_speed = self.rocket_instance.environment_settings["wind speed"]
            self.wind_angle = self.rocket_instance.environment_settings["wind angle"]

            self.reset_stage(rocket_config)

            self.position = np.array([
                float(self.rocket_instance.launch_pad_position.x),
                float(self.rocket_instance.launch_pad_position.y-self.size.y)])
            self.direction = pygame.Vector2()
            self.center_of_pressure = np.array([self.size.x/2,0.0])
            self.center_of_gravity = np.array([self.size.x/2,0.0])

        def reset_stage(self, rocket_config):
            self.rocket_config = rocket_config

            current_stage = self.rocket_instance.current_stage
            self.size = pygame.Vector2( self.rocket_config[str(current_stage)]["size"][0],  self.rocket_config[str(current_stage)]["size"][1])
            self.dry_mass =  self.rocket_config[str(current_stage)]["dry_mass"]
            self.fuel_mass =  self.rocket_config[str(current_stage)]["initial_fuel_mass"]
            self.thrust_position =  self.rocket_config[str(current_stage)]["parts"]["engine"]["position_from_base"] 

        def update(self, time_step):
            self.angle = self.angle % 360

            self.center_of_gravity = np.array(self.get_center_of_gravity)
            self.center_of_pressure = np.array(self.get_center_of_pressure)


            net_force = self.rocket_instance.motor.get_thrust_vector - self.get_weight - self.get_drag
            self.acceleration = net_force/self.get_total_mass
            self.velocity += self.acceleration * time_step

            self.angular_acceleration = self.get_total_torque / self.get_inertia
            self.angular_velocity += self.angular_acceleration * time_step

            angular_velocity_deg = self.angular_acceleration * (180 / np.pi)
            self.angle += angular_velocity_deg * time_step
            self.position[0] -= self.velocity[0]
            self.position[1] -= self.velocity[1]
            self.rocket_instance.rect.center = self.position
            self.direction.y = self.velocity[1]

        @property
        def get_center_of_gravity(self):
            total_mass_rocket = self.get_total_mass

            calculation_each_component = 0
            for component, attrib in self.rocket_config[str(self.rocket_instance.current_stage)]["parts"].items():
                
                position_from_base = attrib["position_from_base"]
                mass = attrib["mass"]
                
                if attrib["shape"] == "cone": 
                    if component == "nose":
                        cg_each_component = position_from_base + attrib["height"]/4
                    else:
                        cg_each_component = position_from_base + attrib["height"]/2
                elif attrib["shape"] == "cylinder":
                    cg_each_component = position_from_base + attrib["height"]/2
                elif attrib["shape"] == "triangle":
                    cg_each_component = position_from_base + attrib["height"]/3
                    mass = mass * attrib["count"]
                else:
                    raise ValueError(f"Unknown shape: {attrib['shape']}")

                calculation_each_component += mass * cg_each_component

            cg_position = calculation_each_component / total_mass_rocket

            return np.array([self.center_of_gravity[0], cg_position])
        @property
        def get_center_of_pressure(self):
            dict_total = {}

            for component, attrib in self.rocket_config[str(self.rocket_instance.current_stage)]["parts"].items():
                if attrib["shape"] == "cylinder":
                    height = attrib["height"]
                    radius = attrib["width"]/2
                    area = 2*np.pi*radius*height
                    position_cg_component = height/2
                    normal_force_coefficient = 0.2

                elif attrib["shape"] == "triangle":
                    base = attrib["width"]
                    height = attrib["height"]
                    area_one_fin = (1/2) * base * height
                    area = area_one_fin * attrib["count"]

                    position_cg_component = attrib["height"]/3
                    normal_force_coefficient = 1.2

                elif attrib["shape"] == "cone":
                    diameter = attrib["width"]
                    radius = diameter/2
                    height = attrib["height"]
                    slant_height = np.sqrt(radius**2 + height**2)
                    area = np.pi*radius*slant_height
                    position_cg_component = height/3
                    normal_force_coefficient = 0.6

                else:
                    raise ValueError(f"Unknown shape: {attrib['shape']}")

                distance_cg_from_base = attrib["position_from_base"]+position_cg_component
                
                dict_total[component] = {
                    "area": area,
                    "normal_c": normal_force_coefficient,
                    "distance_cg_from_base": distance_cg_from_base,
                }

            total_moment = 0
            total_effective_aerodynamic_force = 0

            for component, attrib in dict_total.items():
                contribution = attrib["area"] * attrib["normal_c"] * attrib["distance_cg_from_base"]
                total_moment += contribution
                total_effective_aerodynamic_force += attrib["area"] * attrib["normal_c"]

            if total_effective_aerodynamic_force != 0:
                center_of_pressure_y = total_moment/total_effective_aerodynamic_force
                return np.array([self.center_of_pressure[0],center_of_pressure_y])
            else:
                raise ValueError("total aerodynamic force is zero, invalid CP calculation")
        @property
        def get_cross_sectional_area(self): # TODO implement calculation for different shapes
            if self.angle == 0 or self.angle == 180:
                return np.pi*((self.size.x/2)**2)
            if self.angle == 90 or self.angle == 270:
                return self.size.x*self.size.y
            else:
                angle_in_radians = np.radians(self.angle)
                return (self.size.x * abs(np.sin(angle_in_radians))) + (self.size.y * abs(np.cos(angle_in_radians)))
        @property
        def get_relative_velocity(self):
            return self.velocity - self.get_wind_velocity_vector
        @property
        def get_drag(self):
            speed = np.linalg.norm(self.get_relative_velocity)  
            drag_magnitude = 0.5 * self.drag_coeff * self.get_cross_sectional_area * self.rocket_instance.environment_settings["air density"] * (speed**2)
            drag_direction = self.velocity / speed if speed > 0 else np.array([0.0, 0.0])
            drag = drag_direction * drag_magnitude
            return drag
        @property
        def get_wind_velocity_vector(self):
            return np.array([
                self.wind_speed * np.sin(np.radians(self.wind_angle)),
                self.wind_speed * np.cos(np.radians(self.wind_angle))
            ])
        @property
        def get_total_mass(self):
            return self.dry_mass + self.fuel_mass     
        @property
        def get_weight(self):
            return np.array([0, self.get_total_mass * self.rocket_instance.environment_settings["gravity"]])      
        @property
        def get_torque_thrust(self):
            thrust_vector = np.array([
                self.rocket_instance.motor.get_thrust * np.sin(np.radians(self.rocket_instance.motor.current_angle)),
                self.rocket_instance.motor.get_thrust * np.cos(np.radians(self.rocket_instance.motor.current_angle))
            ])
            lever_arm_vector = self.center_of_gravity - self.thrust_position
            return np.cross(lever_arm_vector, thrust_vector)
        @property
        def get_torque_wind(self):
            lever_arm = self.center_of_gravity - self.center_of_pressure
            wind_vector = self.get_drag
            return np.cross(lever_arm, wind_vector)
        @property
        def get_total_torque(self):
            total_torque = self.get_torque_thrust + self.get_torque_wind
            return total_torque      
        @property
        def get_inertia(self): # TODO: upgrade
            return (1/12) * self.get_total_mass * (3 * np.power(self.size.x/2, 2) + np.power(self.size.y, 2))       
        @property
        def get_AOA_wind(self):            
            # range 0-360 (rocket_angle already in the range)
            angle_rocket = self.angle
            angle_wind = self.wind_angle % 360
            # difference
            relative_nunber = (angle_rocket - angle_wind)%360
            if relative_nunber > 180: relative_nunber -= 360

            return relative_nunber

    class Motor:
        def __init__(self):
            ...

        def reset_variables(self, motor_settings, rocket_instance):
            self.rocket_instance = rocket_instance
            self.current_angle = 0
            self.current_thrust = 0
            self.current_thrust_perc = 0

            self.gravity = self.rocket_instance.environment_settings["gravity"]

            self.reset(motor_settings)

        def reset(self, motor_settings): # TODO: ignition delay, change of isp, num_motors
            current_stage = self.rocket_instance.current_stage

            self.max_thrust = motor_settings[str(current_stage)]["parts"]["engine"]["thrust"]
            self.isp = motor_settings[str(current_stage)]["parts"]["engine"]["isp"]
            self.ignition_delay = motor_settings[str(current_stage)]["parts"]["engine"]["ignition_delay"]
            self.max_angle = motor_settings[str(current_stage)]["parts"]["engine"]["max_angle"]

        def burn_fuel(self, time_step):
            mass_flow_rate = self.get_thrust / (self.isp * self.gravity)
            fuel_consumed = mass_flow_rate * time_step

            if self.rocket_instance.body.fuel_mass >= fuel_consumed:
                self.rocket_instance.body.fuel_mass -= fuel_consumed
                # TODO: csv text (burned fuel each time step)
            else:
                self.rocket_instance.body.fuel_mass = 0
                self.current_thrust_perc = 0            
                # TODO csv test (no enough fuel to sustain burn)

        @property
        def get_thrust(self):
            return (self.current_thrust_perc/100)*self.max_thrust
        @property
        def get_thrust_vector(self):
            angle_radians = np.radians(self.rocket_instance.body.angle)
            thrust_x = self.get_thrust * np.sin(angle_radians)
            thrust_y = self.get_thrust * np.cos(angle_radians)
            return np.array([thrust_x, thrust_y])


    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        super().__init__()

        path_image = '../assets/images/prototype_rockets/test_rocket_small.png'
        self.image = pygame.image.load(path_image).convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect()

        self.body = self.Body()
        self.motor = self.Motor()

    def launch(self, time_step):
        # self.motor.burn_fuel(time_step)
        self.body.update(time_step)

    def controls(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_x]: self.motor.current_thrust_perc = 100 # cut-on
        elif keys[pygame.K_z]: self.motor.current_thrust_perc = 0 # cut-off
        elif keys[pygame.K_w]: self.motor.current_thrust_perc += 1 if self.motor.current_thrust_perc < 100 else 0 # gradually thrust increase
        elif keys[pygame.K_s]: self.motor.current_thrust_perc -= 1 if self.motor.current_thrust_perc > 0 else 0 # gradually thrust decrease
        elif keys[pygame.K_d]: self.motor.current_angle += 1 if self.motor.current_angle < self.motor.max_angle else 0 # gradually change thrust angle +
        elif keys[pygame.K_a]: self.motor.current_angle -= 1 if self.motor.current_angle > -self.motor.max_angle else 0 # grdually change thrust angle -
    
        elif keys[pygame.K_p]: self.body.wind_angle += 1
        elif keys[pygame.K_o]: self.body.wind_angle -= 1

    def collision(self, group_rect: list) -> None:
        if self.body.direction.magnitude() != 0: self.body.direction = self.body.direction.normalize()

        for sprite in group_rect:
            if sprite.rect.colliderect(self.rect):
                if self.body.direction.y < 0:
                    self.rect.bottom = sprite.rect.top
                    self.body.position[0] = self.rect.centerx
                    self.body.position[1] = self.rect.centery
                    self.body.velocity = np.array([0.0, 0.0])

    def render(self, screen, offset):
        scaled_image = pygame.transform.smoothscale(self.copy_image, self.body.size)
        rotated_image = pygame.transform.rotate(scaled_image, self.body.angle)
        self.rect = rotated_image.get_rect(center=self.body.position)

        if offset is not None:
            position = self.rect.topleft - offset
        else:
            position = self.rect.topleft

        screen.blit(rotated_image, position)

        pygame.draw.circle(screen, "red", (self.body.position[0], self.rect.bottomleft[1]-self.body.center_of_pressure[1]), 5) # CP
        pygame.draw.circle(screen, "blue", (self.body.position[0], self.rect.bottomleft[1]-self.body.center_of_gravity[1]), 5) # CM

        center_wind = (
            self.body.position[0]+100 * np.sin(np.radians(self.body.get_AOA_wind-180)),
            self.body.position[1]+100 * np.cos(np.radians(self.body.get_AOA_wind-180))
        )
        pygame.draw.circle(screen, "green", center_wind, 5)


    def restart(self, launch_pad_settings, launch_pad_position):
        self.environment_settings = launch_pad_settings
        self.launch_pad_position = launch_pad_position

        self.current_stage = 1
        with open("../assets/rocket_files/rocket_config_2.json", "r") as file:
            rocket_config = json.load(file)

        self.motor.reset_variables(rocket_config["parts"], self)
        self.body.reset_variables(rocket_config["parts"], self)
