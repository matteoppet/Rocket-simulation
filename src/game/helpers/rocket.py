import pygame
import numpy as np

WORLD_OFFSET = pygame.Vector2(640, 360)

class Physics:
    def __init__(self, rocket_instance, environment):
        self.environment = environment
        self.rocket_instance = rocket_instance

    def apply(self, components_list):
        self.components_list = components_list
        
        self.motor = next((component for component in list(reversed(self.components_list)) if component.name == "motor"), None)

        if self.motor: self.thrust = self.motor.get_thrust
        else: self.thrust = 0

        self.total_mass = 0
        for component in components_list:
            self.total_mass += component.mass

        net_force = self.get_thrust_vector() - self.get_weight - self.get_drag(components_list) - self.get_lift(components_list)
        acceleration = net_force / self.total_mass

        angular_acceleration = self.get_total_torque / self.get_inertia

        return acceleration, angular_acceleration

    def get_center_of_pressure(self):
        temp_data_components = {}
        total_moment = 0
        total_effective_aerodynamic_force = 0

        for component in self.components_list:
            if component.shape == "cylinder":
                radius = component.size.x/2
                area = 2*np.pi*radius*component.size.y
                local_offset_cg = component.size.y/2
                normal_fc = 0.2
            elif component.shape == "cone": 
                radius = component.size.x/2
                slant_height = np.sqrt(radius**2 + component.size.y**2)
                area = np.pi*radius*slant_height
                local_offset_cg = component.size.y/3
                normal_fc = 0.6
            else:
                raise ValueError(f"Unknown shape: {component.shape}")
            
            local_offset_cg_from_nose = component.local_offset.y+local_offset_cg
            temp_data_components[component.name] = {
                "area": area,
                "normal_fc": normal_fc,
                "offset_cg_from_nose": local_offset_cg_from_nose
            }
            
        for component, temp_data in temp_data_components.items():
            contribution = temp_data["area"] * temp_data["normal_fc"] * temp_data["offset_cg_from_nose"]
            total_moment += contribution
            total_effective_aerodynamic_force += temp_data["area"] * temp_data["normal_fc"]

        if total_effective_aerodynamic_force != 0: return np.array([0, total_moment/total_effective_aerodynamic_force])
        else: raise ValueError("Total aerodynamic force is zero, could not process the CoP calculation")

    def get_center_of_gravity(self):
        calculation_each_component = 0
        for component in self.components_list:
            if component.shape == "cone": 
                if component.name == "nose":
                    cg_component = component.local_offset.y + component.size.y/4
                else:
                    cg_component = component.local_offset.y + component.size.y/2
            elif component.shape == "cylinder":
                cg_component = component.local_offset.y + component.size.y/2
            else:
                raise ValueError(f"Unknown shape: {component.shape}")
            
            
            calculation_each_component += component.mass * cg_component
        cg_position = calculation_each_component / self.total_mass
        return np.array([0, cg_position])

    def get_drag(self, components_list):
        air_density = self.environment.get_air_density(self.rocket_instance.get_altitude)
        speed = np.linalg.norm(self.get_relative_velocity)
        cross_sectional_area = self.get_cross_sectional_area(components_list)
        drag_coeff = 0.6 # TODO: Change

        drag_magnitude = 0.5 * drag_coeff * cross_sectional_area * air_density * (speed**2)
        drag_direction = components_list[0].velocity / speed if speed > 0 else np.array([0.0,0.0])
        drag = drag_direction * drag_magnitude
        return drag

    def get_cross_sectional_area(self, components_list):
        fins = None
        for component in components_list:
            if component.name == "fins": 
                number_fins = 4 # TODO: Change
                thickness, height = component.size
                break

        main_area = np.pi*(components_list[0].size.x/2)**2

        if fins: return main_area * (number_fins * thickness * height)
        else: return main_area

    def get_lift(self, components_list):
        fins = None
        for component in components_list:
            if component == "fins":
                aspect_ratio_fins = component.size.y / component.size.x
                fin_efficiency_factor = 2/(1+np.sqrt(1+(aspect_ratio_fins/2)))
                break
        
        air_density = self.environment.get_air_density(self.rocket_instance.get_altitude)
        relative_velocity = self.get_relative_velocity
        angle_of_attack = self.rocket_instance.get_aoa
        cross_sectional_area = self.get_cross_sectional_area(components_list)

        if fins:
            lift_coeff = min((fin_efficiency_factor*np.radians(angle_of_attack)), 2.0)
        else:
            lift_coeff = 0.6 # TODO: Change

        lift = 0.5 * air_density * relative_velocity**2 * lift_coeff * cross_sectional_area
        return lift

    def get_thrust_vector(self):
        return np.array([
            self.thrust * np.sin(np.radians(-self.components_list[0].angle)),
            self.thrust * np.cos(np.radians(-self.components_list[0].angle))
        ])

    def torque_wind(self):
        lever_arm = self.get_center_of_gravity() - self.get_center_of_pressure()
        wind_vector = self.environment.get_wind_velocity_vector
        return np.cross(lever_arm, wind_vector)
    
    def torque_thrust(self):
        thrust_vector = np.array([
            self.thrust * np.sin(np.radians(self.motor.angle)),
            self.thrust * np.cos(np.radians(self.motor.angle))
        ])
        local_offset = self.motor.local_offset
        lever_arm = self.get_center_of_gravity() - local_offset
        return np.cross(lever_arm, thrust_vector)
    
    @property
    def get_total_torque(self):
        if self.motor:
            return self.torque_wind() + self.torque_thrust()
        else:
            return self.torque_wind()

    @property
    def get_inertia(self):
        total_inertia = 0
        for component in self.components_list:
            if component.shape == "cylinder":
                inertia = 0.5 * component.mass * component.size.y * (component.size.x/2)**2
            elif component.shape == "cone":
                inertia = (3/10) * component.mass * (component.size.x/2)**2

            total_inertia += inertia

        return total_inertia

    @property
    def get_relative_velocity(self):
        return self.components_list[0].velocity - self.environment.get_wind_velocity_vector

    @property
    def get_weight(self):
        return np.array([0, self.total_mass * self.environment.get_gravity(self.rocket_instance.get_altitude)])

class Component(pygame.sprite.Sprite):
    def __init__(self, name, parent, attribs, group):
        super().__init__(group)

        self.name = name
        self.parent = parent
        self.child = None
        self.group = group

        self.local_offset = attribs["local_offset"]
        self.size = attribs["size"]
        self.mass = attribs["mass"]
        self.shape = attribs["shape"]

        self.is_attached = True
        self.angle = 0
        self.acceleration = np.array([0.0, 0.0])
        self.velocity = np.array([0.0, 0.0])
        self.angular_velocity = 0

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill("blue")
        self.rect = self.image.get_rect(topleft=WORLD_OFFSET+self.local_offset)

        self.position = pygame.Vector2(self.rect.center[0], self.rect.center[1])

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect)

    def update(self, physics, time_step):
        if self.is_attached:
            if self.parent:
                offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
                offset.rotate_ip(self.parent.angle)

                self.angle = self.parent.angle
                self.position = self.parent.position + offset
            else:
                components = []
                for component in self.group:
                    if component.is_attached:
                        components.append(component)
                    else:
                        break
                acceleration, angular_acceleration = physics.apply(components)
                self.velocity += acceleration * time_step
                self.angular_velocity += angular_acceleration * time_step

                self.position -= self.velocity
                self.angle += self.angular_velocity
        else:
            try: 
                acceleration, angular_acceleration = physics.apply(self.detached_sprites_group_list)
            except AttributeError:
                acceleration, angular_acceleration = physics.apply([self])

            self.velocity += acceleration * time_step
            self.angular_velocity += angular_acceleration * time_step

            self.angle += self.angular_velocity
            self.position -= self.velocity
        
        self.rect.center = self.position

    def detatch(self):
        """ 
            when a component is detatched, it will create a group for all the components below it, 
            it will iterate in a reversed list of the old group of all sprites, (from bottom to top), it will add everything to the new group and stop when it encounter the not attached component,
            and it will copy the velocity from the nose.
        """
        self.detached_sprites_group = pygame.sprite.Group()
        self.is_attached = False

        for sprite in list(reversed(self.group.sprites())):
            if sprite.is_attached:
                self.detached_sprites_group.add(sprite)
            else:
                self.detached_sprites_group.add(sprite)
                break

        self.detached_sprites_group_list = list(reversed(self.detached_sprites_group.sprites()))

        self.velocity = self.group.sprites()[0].velocity.copy()
        self.angular_velocity = self.group.sprites()[0].angular_velocity

class Motor(pygame.sprite.Sprite):
    def __init__(self, name, parent, attribs, group):
        super().__init__(group)
        
        self.name = name
        self.parent = parent
        self.group = group

        self.local_offset = attribs["local_offset"]
        self.size = attribs["size"]
        self.mass = attribs["mass"]
        self.shape = attribs["shape"]

        self.is_attached = True
        self.active = False
        self.angle = 0
        self.max_angle_vectoring = attribs["angle_vectoring"]
        self.max_thrust = attribs["thrust"]
        self.isp = attribs["isp"]

        self.current_thrust_perc = 0

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill("black")
        self.rect = self.image.get_rect(topleft=WORLD_OFFSET+self.local_offset)

        self.position = pygame.Vector2(self.rect.centerx, self.rect.centery)

    def render(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, a, b):
        offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
        offset.rotate_ip(self.parent.angle)

        self.angle = self.parent.angle
        self.position = self.parent.position + offset
        self.rect.center = self.position

    @property
    def get_thrust(self):
        return (self.current_thrust_perc/100)*self.max_thrust

class Rocket:
    def __init__(self, components, environment):
        self.components = components
        self.components_sprite_group = pygame.sprite.Group()
        self.motor_sprite_group = pygame.sprite.Group() 

        parent = None
        for component, attribs in self.components.items():
            if component == "motor":
                Motor(component, parent, attribs, [self.components_sprite_group, self.motor_sprite_group])
            else:
                parent = Component(component, parent, attribs, self.components_sprite_group)

        # TODO: TEMPORARY, implement better activation motor
        self.motor_sprite_group.sprites()[-1].active = True

        self.environment = environment
        self.physics = Physics(self, self.environment)

        self.count = 0
            
    def render(self, screen):
        for component in self.components_sprite_group:
            component.render(screen)

    def update(self, time_step):
        for component in self.components_sprite_group:
            component.update(self.physics, time_step)

    def controls(self):
        keys = pygame.key.get_pressed()

        active_motor = None
        for motor in self.motor_sprite_group:
            if motor.active: active_motor = motor

        if keys[pygame.K_x]: active_motor.current_thrust_perc = 100
        elif keys[pygame.K_z]: active_motor.current_thrust_perc = 0

        if keys[pygame.K_a]: active_motor.angle = 15
        elif keys[pygame.K_d]: active_motor.angle = -15

        if keys[pygame.K_l]:
            component = self.components_sprite_group.sprites()[-2]

            if component.is_attached:
                component.detatch()

    def collision(self):
        raise NotImplementedError

    @property
    def get_altitude(self): # TODO
        return 0
    
    @property
    def get_aoa(self): # TODO
        return 0
    