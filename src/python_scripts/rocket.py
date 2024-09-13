from pygame import Vector2, sprite, image, Rect, transform, key, K_d, K_a, K_w, K_s, K_x, K_z, K_c, time
import ctypes
import math
from numpy import linalg # type: ignore
from math import exp


class RocketBehavior:
    EXPONENTIAL_DECAY_CONSTANT = 0.00693

    def current_state(self, current_world, dt):
        self.current_world = current_world

        if self.touch_ground:
            self.reset()
        else: 
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

            self.physics.update_acceleration(
                self.get_current_gravity,
                self.current_world.drag_coeff,
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
    
    # ! TODO
    @property
    def get_altitude(self):
        return +self.rect.bottomleft[1] - self.current_world.stack_terrain.sprites()[1].rect.topleft[1]

    @property
    def get_actual_thrust_power(self):
        return (self.main_thrust_percentage/100)*self.main_thrust_power

    @property
    def get_current_gravity(self):
        return self.current_world.update_forces(self.altitude)[0]
    
    @property
    def get_thrust_to_weight_ratio(self):
        return self.get_actual_thrust_power / (self.current_mass * self.get_current_gravity)
    
    @property
    def get_current_air_density(self):
        return self.current_world.update_forces(self.altitude)[1]

    @property
    def get_cross_sectional_area(self):
        angle_radians = math.radians(self.angle)
        
        if round(self.angle) in [90, 270]: # facing air with head
            return self.rect.width
        elif round(self.angle) in [0, 180]: # facing air with body
            return self.rect.height
        else:  # for angles
            return abs(self.rect.width * math.cos(angle_radians) + self.rect.height * math.sin(angle_radians))


class Rocket(sprite.Sprite, RocketBehavior):
    def __init__(self, group):
        super().__init__(group)
        sprite.Sprite.__init__(self)

        self.rocket_specifics()

        self.position = Vector2(150, 0)
        self.image = image.load('assets/prototype_2.png').convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = Rect(self.position, self.size)

        # OTHERS
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
        self.size = Vector2(15, 80)

        self.mass = 1000.0
        self.current_mass = self.mass
        self.inertia = ctypes.c_double(0)

        self.main_thrust_power = 80000
        self.lateral_thrust_power = 5000
        self.radius_thrust = self.size.y / 2

        self.initial_fuel = 1
        self.current_fuel = self.initial_fuel


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


    def render(self, screen, offset, zoom_factor):
        # image modification
        rocket_scaled_image = transform.scale(
            self.image,
            (
                int(self.image.get_width() * zoom_factor),
                int(self.image.get_height() * zoom_factor)
            ))
        # calculate offset
        rocket_offset_pos = (self.rect.center - offset) * zoom_factor

        rotated_image = transform.rotate(rocket_scaled_image, self.angle)
        rotated_rect = rotated_image.get_rect(center=rocket_offset_pos)

        self.rect = rotated_rect

        # blit image
        screen.blit(rotated_image, rotated_rect)


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


    def collision(self, group_sprites):
        if sprite.spritecollideany(self, group_sprites):
            self.reset()


    def update_position_angle_rocket(self, dt):
        # update angle
        self.angle += self.angular_vel.value * dt

        # update position
        self.position.x += self.horizontal_vel.value * dt
        self.position.y -= self.vertical_vel.value * dt

        self.rect.topleft = (self.position.x, self.position.y)

# problem altitude