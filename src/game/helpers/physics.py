import numpy as np
import pygame
from typing import Union, Optional


class Physics:
    def __init__(self, rocket_instance, environment):
        self.environment = environment
        self.rocket_instance = rocket_instance

    def apply(self, components: list) -> tuple:
        self.motor = next((component for component in list(reversed(components)) if component.name == "motor"), None)
        if self.motor: self.thrust = self.motor.get_thrust
        else: self.thrust = 0

        total_mass = 0
        for component in components:
            total_mass += component.mass

        net_force = self.get_thrust_vector(components) - self.get_weight(components) - self.get_drag(components) - self.get_lift(components)
        acceleration = net_force / total_mass
        angular_acceleration = self.get_total_torque(components) / self.get_inertia(components)

        return acceleration, angular_acceleration

    def get_center_of_pressure(self, components: list) -> np.ndarray:
        temp_data_components = {}
        total_moment = 0
        total_effective_aerodynamic_force = 0

        for component in components:
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

    def get_center_of_gravity(self, components: list) -> np.ndarray:
        calculation_each_component = 0
        total_mass = 0
        diameter_body = 0
        for component in components:
            if component.shape == "cone": 
                if component.name == "nose":
                    cg_component = component.local_offset.y + component.size.y/4
                else:
                    cg_component = component.local_offset.y + component.size.y/2
            elif component.shape == "cylinder":
                cg_component = component.local_offset.y + component.size.y/2
            else:
                raise ValueError(f"Unknown shape: {component.shape}")
            
            total_mass += component.mass
            calculation_each_component += component.mass * cg_component
            diameter_body = component.size.x/2
        cg_position = calculation_each_component / total_mass
        return np.array([diameter_body, cg_position])
    
    def get_drag(self, components: list) -> list:
        air_density = self.environment.get_air_density(self.rocket_instance.get_altitude(components[0].position[1]))
        speed = np.linalg.norm(self.get_relative_velocity(components))
        cross_sectional_area = self.get_cross_sectional_area(components)
        drag_coeff = 0.6 # TODO: Change

        drag_magnitude = 0.5 * drag_coeff * cross_sectional_area * air_density * (speed**2)
        drag_direction = components[0].velocity / speed if speed > 0 else np.array([0.0,0.0])
        drag = drag_direction * drag_magnitude
        return drag

    def get_cross_sectional_area(self, components: list) -> float:
        fins = None
        for component in components:
            if component.name == "fins": 
                number_fins = 4 # TODO: Change
                thickness, height = component.size
                break

        main_area = np.pi*(components[0].size.x/2)**2

        if fins: return main_area * (number_fins * thickness * height)
        else: return main_area

    def get_lift(self, components: list) -> float:
        fins = None
        for component in components:
            if component == "fins":
                aspect_ratio_fins = component.size.y / component.size.x
                fin_efficiency_factor = 2/(1+np.sqrt(1+(aspect_ratio_fins/2)))
                break
        
        air_density = self.environment.get_air_density(self.rocket_instance.get_altitude(components[0].position[1]))
        relative_velocity = self.get_relative_velocity(components)
        angle_of_attack = self.rocket_instance.get_aoa(components[0])
        cross_sectional_area = self.get_cross_sectional_area(components)

        if fins:
            lift_coeff = min((fin_efficiency_factor*np.radians(angle_of_attack)), 2.0)
        else:
            lift_coeff = 0.6 # TODO: Change

        lift = 0.5 * air_density * relative_velocity**2 * lift_coeff * cross_sectional_area
        return lift
    
    def get_thrust_vector(self, components: list) -> np.ndarray:
        return np.array([
            self.thrust * np.sin(np.radians(-components[0].angle)),
            self.thrust * np.cos(np.radians(-components[0].angle))
        ])

    def torque_wind(self, components: list) -> float:
        lever_arm = self.get_center_of_gravity(components) - self.get_center_of_pressure(components)
        wind_vector = self.environment.get_wind_velocity_vector
        return np.cross(lever_arm, wind_vector)
    
    def torque_thrust(self, components: list) -> float:
        thrust_vector = np.array([
            self.thrust * np.sin(np.radians(-self.motor.angle)),
            self.thrust * np.cos(np.radians(-self.motor.angle))
        ])
        local_offset = self.motor.local_offset
        lever_arm = self.get_center_of_gravity(components) - local_offset
        return np.cross(lever_arm, thrust_vector)
    
    def get_inertia(self, components: list) -> float:
        total_inertia = 0
        for component in components:
            if component.shape == "cylinder":
                inertia = 0.5 * component.mass * component.size.y * (component.size.x/2)**2
            elif component.shape == "cone":
                inertia = (3/10) * component.mass * (component.size.x/2)**2

            total_inertia += inertia

        return total_inertia
    
    def get_weight(self, components: float) -> np.ndarray:
        total_mass = 0
        for component in components:
            total_mass += component.mass

        return np.array([0, total_mass * self.environment.get_gravity(self.rocket_instance.get_altitude(components[0].position[1]))])
    
    def get_relative_velocity(self, components: list) -> np.ndarray:
        return components[0].velocity - self.environment.get_wind_velocity_vector

    def get_total_torque(self, components: list) -> float:
        if self.motor:
            return self.torque_wind(components) + self.torque_thrust(components)
        else:
            return self.torque_wind(components)
        

    def free_fall_object_with_collision(self, object1: pygame.sprite.Sprite, object2_list: list, time_step: int, components: list):
        object2 = object2_list[-1]
        collision_point  = pygame.sprite.collide_mask(object1, object2)
        pivot_point = np.array([collision_point[0], collision_point[1]])
        object1_center_of_mass = self.get_center_of_gravity([object1])
        force = self.get_weight([object1])

        lever_arm = object1_center_of_mass - pivot_point
        torque = lever_arm * force

        angular_acceleration = torque / self.get_inertia([object1])
        print(object1.name)
        # stop object to fall continusly
        # calculate angular acceleration
        # change angular acceleration object 

        # write elegant code