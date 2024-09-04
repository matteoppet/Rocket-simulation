from pygame import sprite, Surface, transform, image, key, time, Vector2, K_d, K_a, K_w, K_s, K_x, K_z, font, draw, Rect

import ctypes
import math
from numpy import linalg # type: ignore


class Rocket(sprite.Sprite):
    def __init__(self, world, group):
        super().__init__(group)
        sprite.Sprite.__init__(self)

        self.world = world

        # setup rocket
        self.size = (10, 80)
        self.position = Vector2(self.world.size[0]/2, self.world.position.y-self.size[1])

        self.image = image.load('assets/prototype_2.png').convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = Rect(self.position, self.size)

        # ! ROCKET SPECIFICS
        self.mass = 100.0
        self.max_thrust = 5000 # newtons
        # create all variables
        self.reset()

        self.fontt = font.SysFont("Helvetica", 18)

        self.setup_c_files()


    def setup_c_files(self):
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


    def current_state(self, dt):
        # calculate speed
        self.speed = math.sqrt(self.vertical_vel.value**2+self.horizontal_vel.value**2)

        # calculate distance from terrain
        self.altitude = self.world.rect.topleft[1] - self.rect.bottomleft[1]
        
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
                self.world.drag_coeff,
                self.world.gravity,
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

        self.rect.topleft = (self.position.x, self.position.y)

        
    def render(self, screen, offset, zoom_factor):
        # image modification
        rocket_scaled_image = transform.scale(
            self.image,
            (
                int(self.image.get_width() * zoom_factor),
                int(self.image.get_height() * zoom_factor)
            ))
        rocket_scaled_image = transform.rotate(rocket_scaled_image, self.angle)

        # calculate offset
        rocket_offset_pos = (self.rect.topleft - offset) * zoom_factor

        # blit image
        screen.blit(rocket_scaled_image, rocket_offset_pos)


    def reset(self):
        self.angle = 90
        self.thrust_percentage = 0
        self.horizontal_vel = ctypes.c_double(0)
        self.vertical_vel = ctypes.c_double(0)
        self.horizontal_acc = ctypes.c_double(0)
        self.vertical_acc = ctypes.c_double(0)
        self.speed = 0

        self.on_platform = True
        self.collision = False

        self.altitude = 0

        self.t_minus = 0


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