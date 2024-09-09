from pygame import sprite, Surface, transform, image, key, time, Vector2, K_d, K_a, K_w, K_s, K_x, K_z, font, draw, Rect

import ctypes
import math
from numpy import linalg # type: ignore



class Rocket(sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        sprite.Sprite.__init__(self)

        # setup rocket
        self.size = Vector2(15, 80)
        self.position = Vector2(150,0)

        self.image = image.load('assets/prototype_2.png').convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = Rect(self.position, self.size)

        # ! ROCKET SPECIFICS
        self.mass = 1000.0
        self.inertia = 552083.33
        self.radius_thrust = self.size.y/2
        self.lateral_thrust_power = 5000 # newtons
        self.max_main_thrust = 50000 # newtons
        self.reset()

        """ if changing rocket
        - Change mass
        - Change inertia
        - Change radius thrust
        - Change power main/lateral thrust
        """

        self.fontt = font.SysFont("Helvetica", 18)

        self.setup_c_files()

        self.start_time = time.get_ticks()


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


    def controls(self, timerevent):
        keys = key.get_pressed()

        self.thrust_force = 0

        if keys[K_d]:
            self.lateral_thrust_force = self.lateral_thrust_power
            self.time_lateral_thrust = round(((time.get_ticks() - self.start_time)//2)/1000)
        elif keys[K_a]:
            self.lateral_thrust_force = -self.lateral_thrust_power
            self.time_lateral_thrust = round(((time.get_ticks() - self.start_time)//2)/1000)
        else:
            self.time_lateral_thrust = 0
        
        if keys[K_w]:
            if self.on_platform:
                self.on_platform = False

            if self.main_thrust_percentage >= 100:
                self.main_thrust_percentage = 100
            else:
                self.main_thrust_percentage += 1
        
        if keys[K_s]:
            if self.main_thrust_percentage <= 0:
                self.main_thrust_percentage = 0
            else:
                self.main_thrust_percentage -= 1
        if keys[K_x]:
            self.on_platform = False
            self.main_thrust_percentage = 100

            time.set_timer(timerevent, 1000)
        if keys[K_z]:
            self.main_thrust_percentage = 0



    def current_state(self, current_world, dt):
        self.world = current_world

        # calculate speed
        self.speed = math.sqrt(self.vertical_vel.value**2+self.horizontal_vel.value**2)

        # calculate distance from terrain
        self.altitude = self.world.stack_terrain.sprites()[1].rect.topleft[1] - self.rect.bottomleft[1]
        
        # update on_platform variable when applying thrust
        if self.on_platform:
            self.vertical_vel.value = 0
            self.horizontal_vel.value = 0
        else:
            actual_thrust = (self.main_thrust_percentage/100)*self.max_main_thrust # convert actual thrust applied

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

            # calculate torque
            self.physics.calculate_torque(
                self.lateral_thrust_force,
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
                self.time_lateral_thrust,
                self.angular_vel,
            )

            # update angle
            self.angle += self.angular_vel.value * dt

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
        # calculate offset
        rocket_offset_pos = (self.rect.center - offset) * zoom_factor

        rotated_image = transform.rotate(rocket_scaled_image, self.angle)
        rotated_rect = rotated_image.get_rect(center=rocket_offset_pos)

        # blit image
        screen.blit(rotated_image, rotated_rect)


    def reset(self):
        self.torque = ctypes.c_double(0)
        self.angle = 90
        self.lateral_thrust_force = 0

        # acceleration variables
        self.angular_acc = ctypes.c_double(0)
        self.horizontal_acc = ctypes.c_double(0)
        self.vertical_acc = ctypes.c_double(0)

        # velocity variables
        self.horizontal_vel = ctypes.c_double(0)
        self.vertical_vel = ctypes.c_double(0)
        self.angular_vel = ctypes.c_double(0)
        self.speed = 0

        # others
        self.on_platform = True
        self.collision = False
        self.altitude = 0
        self.t_minus = 0
        self.main_thrust_percentage = 0


    def debug(self, screen, clock):
        text_accelerations = self.fontt.render(f'Acceleration: h:{round(self.horizontal_acc.value, 3)}, v:{round(self.vertical_acc.value, 3)}', False, "black")
        text_velocities = self.fontt.render(f'Velocity: h:{round(self.horizontal_vel.value,3)}, v:{round(self.vertical_vel.value,3)}', False, "black")
        text_thrust = self.fontt.render(f'Thrust: {self.main_thrust_percentage}', False, "black")
        text_on_platform = self.fontt.render(f'On platform: {self.on_platform}', False, "black")
        text_altitude = self.fontt.render(f'Altitude: {self.altitude}m', False, "black")
        text_speed = self.fontt.render(f"Velocity: {round(self.speed,1)} m/s", False, "black")
        text_time = self.fontt.render(f"T-minus: {self.t_minus}s", False, "black")
        text_fps = self.fontt.render(f"FPS: {round(clock.get_fps(),1)}", False, "black")

        starting_y = 20
        starting_x = 20
        
        screen.blit(text_accelerations, (starting_x, starting_y))
        screen.blit(text_velocities, (starting_x, starting_y+20))
        screen.blit(text_thrust, (starting_x, starting_y+40))
        screen.blit(text_on_platform, (starting_x, starting_y+60))
        screen.blit(text_altitude, (starting_x, starting_y+100))
        screen.blit(text_speed, (starting_x, starting_y+120))
        screen.blit(text_time, (starting_x, starting_y+140))
        screen.blit(text_fps, (starting_x, starting_y+160))
