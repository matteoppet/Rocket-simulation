import pygame 
from settings import *
import math

class RocketCalculation:
    EXPONENTIAL_DECAY_CONSTANT = 0.02 # search docs rockets engines

    def calculate_state(self, dt):
        # check parts
        if self.get_weight.y > self.max_thrust_power:
            print("ERROR: Thrust power too lower for the weight of the rocket")
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)

        self.calculate_acceleration()
        self.calculate_velocity(dt)

        print(self.position, self.rect, self.direction, self.velocity)

        self.position -= self.velocity
        self.rect.center = self.position
        self.direction.y = self.velocity.y

        # self.calculate_angular_acceleration()
        # self.calculate_angular_velocity(dt)

        # self.thrust_vector = pygame.Vector2(0, self.current_thrust_power).rotate(self.current_gimbal_angle)


    def calculate_acceleration(self):
        self.acceleration = self.get_resultance_force/self.mass
    
    def calculate_velocity(self, dt):
        self.velocity += self.acceleration * dt



    @property
    def get_weight(self): # return newton (weight(kg) * gravity)
        return pygame.Vector2(0, self.mass * GRAVITY)
    @property
    def get_resultance_force(self): # return newton (thrustx-weight)
        return self.thrust_vector - self.get_weight


class Rocket(pygame.sprite.Sprite, RocketCalculation):
    def __init__(self):
        self.size = pygame.Vector2(10, 80)
        self.start_position = pygame.Vector2(200, 700)

        self.image = pygame.image.load("assets/prototype.png").convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.start_position.x, self.start_position.y))

        self.reset()

        self.direction = pygame.Vector2(0,0)


    def reset(self):
        self.legs = True
        self.rocket_angle = 0
        self.rocket_orientation = 0
        self.position = pygame.Vector2(self.start_position.x, self.start_position.y)


        self.mass = 10
        self.fuel = 1000.0
        self.current_mass = self.mass
        self.current_fuel = self.fuel
        self.reference_area = self.rect.width * self.rect.height
        self.radius_thrust = self.size.y/2

        self.altitude = 0
        self.speed = 0
        self.TWR = 0
        self.torque = 0

        self.acceleration = pygame.Vector2(0,0)
        self.velocity = pygame.Vector2(0, 0)

        self.max_thrust_power = 120 # newton
        self.current_thrust_power = 0
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)


    def controls(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_x]:
            self.current_thrust_power = self.max_thrust_power
        elif keys[pygame.K_z]:
            self.current_thrust_power = 0

        if keys[pygame.K_d]:
            ...
        if keys[pygame.K_a]:
            ...
 

    def collision(self, platform):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        if platform.colliderect(self.rect):
            if self.direction.y < 0:

                self.rect.bottom = platform.top
                self.position.y = self.rect.bottom-self.size.y/2
                self.velocity = pygame.Vector2(0,0)

            if self.direction.y > 0:
                self.rect.top = platform.bottom


    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.copy_image, self.rocket_angle)
        screen.blit(rotated_image, self.rect)
    


# create collision

# acceration (no drag, no mass changed) DONE
# velocity based on acceleration DONE

# implement rocket simulation graphic (and rotate it) (AFTER)
# angular velocity (i.e. the rocket continues to rotate if the gimbal rocket is always to the right) 
# rotate the thrust based on the angle of the gimbal rocket
# rotate the rocket based on the angle of which is pointed the rocket

# angle thrust rocket and change horizontal acc and vel 

# make choice do add gravity and mass changes
# acceleration (with drag and mass changes)