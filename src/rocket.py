from pygame import sprite, Surface, transform, image, key, time, Vector2, K_d, K_a, K_w, K_s, K_x, K_z, font, draw

import ctypes
import math
from numpy import linalg


class Rocket(sprite.Sprite):
    def __init__(self, height_floor, group):
        super().__init__(group)
        sprite.Sprite.__init__(self)

        # setup rocketd
        initial_height = 80
        initial_position = (500, height_floor-(initial_height/2))
        self.image = image.load('assets/prototype_2.png').convert_alpha()
        self.copy_image = self.image
        self.rect = self.copy_image.get_rect(center=initial_position)

        # constants
        self.mass = 100.0
        self.drag_coefficient = 0.1 # air resistance
        
        # variables
        self.angle = 90
        self.vertical_vel = ctypes.c_double(0)
        self.horizontal_vel = ctypes.c_double(0)
        self.vertical_acc = ctypes.c_double(0)
        self.horizontal_acc = ctypes.c_double(0)
        self.thrust_percentage = 0
        self.speed = 0
        self.max_thrust = 5000 # newtons
        self.altitude = 0
        self.t_minus = 0

        self.position = Vector2(initial_position)

        # setup c files
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

        self.on_platform = True
        self.collision = True

        self.fontt = font.SysFont("Helvetica", 18)


    def rotate(self):
        # rotate the image using the original image resetting the angle
        self.copy_image = transform.rotate(self.image, self.angle)
        self.rect = self.copy_image.get_rect(center=self.rect.center)


    def controls(self, timerevent):
        keys = key.get_pressed()

        if keys[K_d]:
            self.angle += 1
        if keys[K_a]:
            self.angle -= 1
        if keys[K_w]:
            if self.on_platform:
                self.on_platform = False

            if self.thrust_percentage >= 100:
                self.thrust_percentage = 100
            else:
                self.thrust_percentage += 1
        
        if keys[K_s]:
            if self.thrust_percentage <= 0:
                self.thrust_percentage = 0
            else:
                self.thrust_percentage -= 1
        if keys[K_x]:
            self.on_platform = False
            self.thrust_percentage = 100

            time.set_timer(timerevent, 1000)
        if keys[K_z]:
            self.thrust_percentage = 0


    def current_state(self, dt, gravity, floor_position):
        # calculate speed
        self.speed = math.sqrt(self.vertical_vel.value**2+self.horizontal_vel.value**2)

        # calculate distance from terrain
        self.altitude = linalg.norm(self.position - floor_position)
        
        # update on_platform variable when applying thrust
        if self.on_platform:
            self.vertical_vel.value = 0
            self.horizontal_vel.value = 0
        else:
            actual_thrust = (self.thrust_percentage/100)*self.max_thrust # convert actual thrust applied

            # update acceleration
            self.physics.update_acceleration(
                self.mass,
                actual_thrust,
                self.drag_coefficient,
                gravity,
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

        # update position
        self.position.x += self.horizontal_vel.value * dt
        self.position.y -= self.vertical_vel.value * dt

        self.rect.center = (self.position.x, self.position.y)


    def debug(self, screen):
        text_accelerations = self.fontt.render(f'Acceleration: h:{round(self.horizontal_acc.value, 3)}, v:{round(self.vertical_acc.value, 3)}', False, "black")
        text_velocities = self.fontt.render(f'Velocity: h:{round(self.horizontal_vel.value,3)}, v:{round(self.vertical_vel.value,3)}', False, "black")
        text_thrust = self.fontt.render(f'Thrust: {self.thrust_percentage}', False, "black")
        text_on_platform = self.fontt.render(f'On platform: {self.on_platform}', False, "black")
        text_altitude = self.fontt.render(f'Altitude: {self.altitude}m', False, "black")
        text_speed = self.fontt.render(f"Velocity: {round(self.speed,1)} m/s", False, "black")
        text_time = self.fontt.render(f"T-minus: {self.t_minus}s", False, "black")

        starting_y = 20
        starting_x = 20
        
        screen.blit(text_accelerations, (starting_x, starting_y))
        screen.blit(text_velocities, (starting_x, starting_y+20))
        screen.blit(text_thrust, (starting_x, starting_y+40))
        screen.blit(text_on_platform, (starting_x, starting_y+60))
        screen.blit(text_altitude, (starting_x, starting_y+100))
        screen.blit(text_speed, (starting_x, starting_y+120))
        screen.blit(text_time, (starting_x, starting_y+140))


        

    def render(self, screen, dt):
        self.rotate()

        self.rect.center = (self.position.x, self.position.y)

        draw.rect(screen, "red", self.rect)
        screen.blit(self.copy_image, self.rect.topleft)


    def reset(self):
        self.angle = 90
        self.thrust_percentage = 0
        self.horizontal_vel.value = 0
        self.vertical_vel.value = 0
        self.horizontal_acc.value = 0
        self.vertical_acc.value = 0

        self.on_platform = True
        self.collision = False