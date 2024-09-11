from pygame import Vector2, sprite, image, Rect, transform, key, K_d, K_a, K_w, K_s, K_x, K_z, time
import ctypes
import math
from numpy import linalg # type: ignore

class Rocket(sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        sprite.Sprite.__init__(self)

        # ROCKET SPECIFICS
        self.size = Vector2(15, 80)
        self.position = Vector2(150, 0)
        self.mass = 1000.0
        self.inertia = 552083.33
        self.radius_thrust = self.size.y/2
        self.main_thrust_power = 50000
        self.lateral_thrust_power = 5000

        self.image = image.load('assets/prototype_2.png').convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = Rect(self.position, self.size)

        # OTHERS
        self.c_functions()
        self.reset()
        self.start_time = time.get_ticks()

        """ if changing rocket
        - Change mass
        - Change inertia
        - Change radius thrust
        - Change power main/lateral thrust
        """


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


    def reset(self):
        self.angular_acc = ctypes.c_double(0)
        self.angular_vel = ctypes.c_double(0)
        
        self.horizontal_acc = ctypes.c_double(0)
        self.horizontal_vel = ctypes.c_double(0)

        self.vertical_acc = ctypes.c_double(0)
        self.vertical_vel = ctypes.c_double(0)

        self.torque = ctypes.c_double(0)
        self.angle = 90

        self.altitude = 0
        self.time = 0
        self.touch_ground = False

        self.main_thrust_percentage = 0
        self.lateral_thrust_percentage = 0


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

        # blit image
        screen.blit(rotated_image, rotated_rect)


    def current_state(self, current_world, dt):
        self.speed = math.sqrt(self.vertical_vel.value**2+self.horizontal_vel.value**2)
        self.altitude = current_world.stack_terrain.sprites()[1].rect.topleft[1] - self.rect.bottomleft[1]

        if self.touch_ground:
            self.reset()
        else:
            actual_thrust = (self.main_thrust_percentage/100)*self.main_thrust_power

            # update acceleration
            self.physics.update_acceleration(
                self.mass,
                actual_thrust,
                current_world.drag_coeff,
                current_world.gravity,
                self.angle,
                self.horizontal_vel.value,
                self.vertical_vel.value,
                self.horizontal_acc,
                self.vertical_acc
            )

            # update velocity
            self.physics.update_velocity(
                self.horizontal_acc.value,
                self.vertical_acc.value,
                dt,
                self.horizontal_vel.value,
                self.vertical_vel.value,
                self.horizontal_vel,
                self.vertical_vel
            )

            # calculate torque
            self.physics.calculate_torque(
                self.lateral_thrust_percentage,
                self.radius_thrust,
                self.torque
            )

            # update angular acceleration
            self.physics.update_angular_acceleration(
                self.torque,
                self.inertia,
                self.angular_acc
            )

            # update angular velocity
            self.physics.update_angular_velocity(
                self.angular_acc,
                self.time_lateral_thrust_activated,
                self.angular_vel,
            )

        # update angle
        self.angle += self.angular_vel.value * dt

        # update position
        self.position.x += self.horizontal_vel.value * dt
        self.position.y -= self.vertical_vel.value * dt

        self.rect.topleft = (self.position.x, self.position.y)


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
            

        # Cut-on Cut-off main thrust
        if keys[K_x]:
            if self.touch_ground: self.touch_ground = False
            self.main_thrust_percentage = 100
        elif keys[K_z]:
            self.main_thrust_percentage = 0


    def collision(self, group_sprites):
        if sprite.spritecollideany(self, group_sprites):
            self.reset()