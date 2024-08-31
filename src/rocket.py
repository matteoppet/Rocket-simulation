from pygame import sprite, Surface, transform, image, key, time, Vector2, K_d, K_a, K_w, K_s

import ctypes


class Rocket(sprite.Sprite):
    def __init__(self, height_floor):
        # setup rocket
        initial_height = 80
        initial_position = (500, height_floor-(initial_height/2))
        self.image = image.load('assets/prototype.png').convert_alpha()
        self.copy_image = self.image
        self.rect = self.copy_image.get_rect(center=initial_position)

        # constants
        self.mass = 100
        self.drag_coefficient = 1 # air resistance
        
        # variables
        self.angle = 90
        self.vertical_vel = ctypes.c_double(0)
        self.horizontal_vel = ctypes.c_double(0)
        self.vertical_acc = ctypes.c_double(0)
        self.horizontal_acc = ctypes.c_double(0)
        self.thrust = 0
        
        self.dt = 0
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


        self.on_plaftorm = True


    def rotate(self):
        # rotate the image using the original image resetting the angle
        self.copy_image = transform.rotate(self.image, self.angle-90)
        self.rect = self.copy_image.get_rect(center=self.rect.center)


    def controls(self):
        keys = key.get_pressed()

        if keys[K_d]:
            self.angle += 1
        if keys[K_a]:
            self.angle -= 1
        if keys[K_w]:
            if self.on_plaftorm:
                self.on_plaftorm = False

            self.thrust += 1
        if keys[K_s]:
            if self.thrust <= 0:
                self.thrust = 0
            else:
                self.thrust -= 1


    def update_position(self, dt, gravity):
        # updating delta time
        self.dt = dt
        
        if self.on_plaftorm:
            self.vertical_vel.value = 0
            self.horizontal_vel.value = 0
        else:
            # update acceleration
            self.physics.update_acceleration(
                self.mass,
                self.thrust,
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
                self.dt,
                self.horizontal_vel.value,
                self.vertical_vel.value,
                self.horizontal_vel,
                self.vertical_vel
            )

        # update position
        self.position.x += self.horizontal_vel.value * self.dt
        self.position.y -= self.vertical_vel.value * self.dt

        self.rect.center = (self.position.x, self.position.y)


    def debug(self):
        print(f"Vertical acc/vel: {self.vertical_acc.value} / {self.vertical_vel.value}, Horizontal acc/vel: {self.horizontal_acc.value} / {self.horizontal_vel.value}, Thrust: {self.thrust}")


    def draw(self, screen):
        screen.blit(self.copy_image, self.rect.topleft)