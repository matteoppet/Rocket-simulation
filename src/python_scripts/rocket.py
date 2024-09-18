from pygame import Vector2, sprite, image, Rect, transform, key, K_d, K_a, K_w, K_s, K_x, K_z, K_c, K_r, time
import ctypes
import math
from numpy import linalg # type: ignore
from math import exp
from settings import *


class RocketCalculations:
    EXPONENTIAL_DECAY_CONSTANT = 0.02 # search docs rockets engines

    def current_state(self, environment, current_planet, dt):
        self.environment = environment
        self.current_planet = current_planet

        self.dt = dt

        if self.main_thrust_percentage > 0:
            if self.time_main_thrust_activated == 0:
                self.start_time_main_thrust = time.get_ticks()
            self.time_main_thrust_activated = round(((time.get_ticks() - self.start_time)//2)/1000)
        else:
            self.time_main_thrust_activated = self.time_main_thrust_activated

        self.current_mass = self.mass - self.get_current_mass
        self.speed = self.get_speed
        self.actual_power = self.get_actual_thrust_power

        if self.get_fuel_remaining <= 0:
            self.actual_power = 0

        if self.get_altitude < 200:
            self.deploy_legs = True
        else: self.deploy_legs = False

        self.physics.update_acceleration(
            self.get_current_gravity,
            self.get_drag_coeff,
            self.get_current_air_density,
            self.get_cross_sectional_area,
            self.current_mass,
            self.angle,
            self.actual_power,
            self.horizontal_vel.value,
            self.vertical_vel.value,
            self.horizontal_acc,
            self.vertical_acc
        )

        self.physics.update_velocity(
            self.horizontal_acc.value,
            self.vertical_acc.value,
            self.dt,
            self.horizontal_vel.value,
            self.vertical_vel.value,
            self.horizontal_vel,
            self.vertical_vel
        )

        self.physics.calculate_torque(
            self.lateral_thrust_percentage, self.radius_thrust, self.torque
        )

        self.physics.calculate_inertia(
            self.size.x, self.size.y, self.current_mass, self.inertia
        )

        self.physics.update_angular_acceleration(
            self.torque, self.inertia.value, self.angular_acc
        )

        self.physics.update_angular_velocity(
            self.angular_acc, self.time_lateral_thrust_activated, self.angular_vel
        )


    @property
    def get_fuel_remaining(self):
        return self.initial_fuel * exp(-self.EXPONENTIAL_DECAY_CONSTANT * self.time_main_thrust_activated)

    @property
    def get_current_mass(self):
        return self.mass - (self.mass * exp(-self.EXPONENTIAL_DECAY_CONSTANT * self.time_main_thrust_activated))
    
    @property
    def get_speed(self):
        return math.sqrt(self.vertical_vel.value**2+self.horizontal_vel.value**2)
    
    @property
    def get_altitude(self):
        return -self.position.y + self.environment.rects_environment["platform"].topleft[1]

    @property
    def get_actual_thrust_power(self):
        return (self.main_thrust_percentage/100)*self.main_thrust_power

    @property
    def get_current_gravity(self):
        return self.environment.update_forces(self.altitude, self.environment.current_world)[0]
    
    @property
    def get_thrust_to_weight_ratio(self):
        return self.get_actual_thrust_power / (self.current_mass * self.get_current_gravity)
    
    @property
    def get_current_air_density(self):
        return self.environment.update_forces(self.altitude, self.environment.current_world)[1]

    @property
    def get_cross_sectional_area(self):
        angle_radians = math.radians(self.angle)
        
        if round(self.angle) in [90, 270]: # facing air with head
            return self.rect.width
        elif round(self.angle) in [0, 180]: # facing air with body
            return self.rect.height
        else:  # for angles
            return abs(self.rect.width * math.cos(angle_radians) + self.rect.height * math.sin(angle_radians))

    @property
    def get_drag_coeff(self):
        if round(self.angle) > 45 and round(self.angle) < 135 or round(self.angle) > 225 and round(self.angle) > -45:
            return self.environment.planets_data[self.current_planet]["drag_coeff"]
        elif round(self.angle) < 45 and round(self.angle) > -45 or round(self.angle) > 135 and round(self.angle) < 225:
            return self.environment.planets_data[self.current_planet]["drag_coeff"]+2
        else:
            return self.environment.planets_data[self.current_planet]["drag_coeff"]

    @property
    def get_mach_number(self):
        return self.speed / 340.2 # m/s=343.2 km/h = 1235.6



class Rocket(sprite.Sprite, RocketCalculations):
    def __init__(self):
        super().__init__()
        sprite.Sprite.__init__(self)

        self.rocket_specifics()

        # 150, -44
        self.starting_position = (200, 800)

        self.position = Vector2(self.starting_position)
        self.image = image.load('assets/prototype_2.png').convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = Rect(self.position, self.size)

        self.c_functions()
        self.reset()
        self.start_time = time.get_ticks()
        self.start_time_main_thrust = time.get_ticks()

        """ if changing rocket
        - Change mass
        - Change inertia
        - Change radius thrust
        - Change power main/lateral thrust
        """


    def rocket_specifics(self):
        self.size = Vector2(17, 209)

        self.mass = 1000.0
        self.current_mass = self.mass
        self.inertia = ctypes.c_double(0)

        self.main_thrust_power = 80000
        self.lateral_thrust_power = 5000
        self.radius_thrust = self.size.y / 2

        self.initial_fuel = 1000 # kg
        self.current_fuel = self.initial_fuel

        self.deploy_legs = True


    def c_functions(self):
        self.physics = ctypes.CDLL('././lib/physics.dll')
        self.physics.update_acceleration.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double)
        ]
        self.physics.update_velocity.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double)
        ]
        self.physics.calculate_torque.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.physics.update_angular_acceleration.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.physics.update_angular_velocity.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.physics.calculate_inertia.argtypes = [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double)
        ]


    def reset(self):
        self.angular_acc = ctypes.c_double(0)
        self.angular_vel = ctypes.c_double(0)
        
        self.horizontal_acc = ctypes.c_double(0)
        self.horizontal_vel = ctypes.c_double(0)

        self.vertical_acc = ctypes.c_double(0)
        self.vertical_vel = ctypes.c_double(0)

        self.torque = ctypes.c_double(0)
        self.angle = 90

        self.speed = 0
        self.altitude = 0
        self.time = 0
        self.touch_ground = True
        self.TWR = 0

        self.cross_sectional_area = self.rect.width * self.rect.height

        self.inertia = ctypes.c_double(0)

        self.main_thrust_percentage = 0
        self.lateral_thrust_percentage = 0

        self.time_main_thrust_activated = 0

        self.position = Vector2(self.starting_position)


    def render(self, screen):
        rotated_image = transform.rotate(self.image.copy(), self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)

        self.rect = rotated_rect

        # blit image
        screen.blit(rotated_image, self.rect)


    def controls(self):
        keys = key.get_pressed()

        # Fire lateral thrusts
        if keys[K_d]:
            self.lateral_thrust_percentage = self.lateral_thrust_power
            self.time_lateral_thrust_activated = round(((time.get_ticks() - self.start_time)//2)/1000)
        elif keys[K_a]:
            self.lateral_thrust_percentage = -self.lateral_thrust_power
            self.time_lateral_thrust_activated = round(((time.get_ticks() - self.start_time)//2)/1000)
        else:
            self.time_lateral_thrust_activated = 0
        
        # Fire main thrust
        if keys[K_w]:
            if self.touch_ground: self.touch_ground = False

            if self.main_thrust_percentage >= 100: 
                self.main_thrust_percentage = 100
            else: 
                self.main_thrust_percentage += 1
        elif keys[K_s]:
            if self.main_thrust_percentage <= 0:
                self.main_thrust_percentage = 0
            else:
                self.main_thrust_percentage -= 1

        # cut on main thrust
        if keys[K_x]:
            if self.touch_ground: self.touch_ground = False
            self.main_thrust_percentage = 100
        # cut off main thrust
        elif keys[K_z]:
            self.main_thrust_percentage = 0
        # cut lateral thrust
        elif keys[K_c]:
            self.lateral_thrust_percentage = 0

        if keys[K_r]:
            self.reset()


    def collision(self, platform_rect):
        if self.rect.colliderect(platform_rect):
            self.horizontal_acc.value = 0
            self.horizontal_vel.value = 0

            self.vertical_acc.value = 0
            self.vertical_vel.value = 0


    def update_position_angle_rocket(self, dt):
        # update angle
        self.angle += self.angular_vel.value * dt

        # update position
        self.position.x += self.horizontal_vel.value * dt
        self.position.y -= self.vertical_vel.value * dt

        self.rect.center = (self.position.x, self.position.y)


"""
1. Create the only rocket launch for now. rocket launch test, then come back to earth
2. add the recovery possibility, add the parachute
2.5 add the autopilot button (i.e. computer boar)
3. add the planets and the orbitals as map where you can choose where to start
4. then think if do the whole game
"""