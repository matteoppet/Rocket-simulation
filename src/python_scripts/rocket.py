import pygame 
from settings import *
import math
import time

class RocketCalculation:
    EXPONENTIAL_DECAY_CONSTANT = 0.02 # search docs rockets engines

    def calculate_state(self, dt):
        # check parts
        if self.get_weight.y > self.max_thrust_power:
            print("ERROR: Thrust power too lower for the weight of the rocket")
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)

        self.calculate_acceleration()
        self.calculate_velocity(dt)
        self.calculate_angular_acceleration()
        self.calculate_angular_velocity(dt)

        angular_velocity_deg = self.angular_acceleration * (180 / math.pi)
        self.rocket_angle += angular_velocity_deg * dt
        self.position -= self.velocity
        self.rect.center = self.position
        self.direction.y = self.velocity.y

    def calculate_acceleration(self):
        rocket_angle_radians = math.radians(self.rocket_angle)
        thrust_x = self.current_thrust_power * math.sin(rocket_angle_radians)
        thrust_y = self.current_thrust_power * math.cos(rocket_angle_radians)

        self.thrust_vector = pygame.Vector2(thrust_x, thrust_y)

        self.acceleration = self.get_resultance_force/self.mass
    
    def calculate_velocity(self, dt):
        self.velocity += self.acceleration * dt

    def calculate_angular_acceleration(self): # returns radians
        self.angular_acceleration = self.get_torque / self.get_inertia

    def calculate_angular_velocity(self, dt):
        self.angular_velocity = self.angular_acceleration * dt


    @property
    def get_weight(self): # return newton (weight(kg) * gravity)
        return pygame.Vector2(0, self.mass * GRAVITY)
    @property
    def get_resultance_force(self): # return newton (thrustx-weight)
        return self.thrust_vector - self.get_weight
    @property
    def get_torque(self):
        return self.current_thrust_power * 40 * math.sin(self.gimbal_angle)
    @property
    def get_inertia(self):
        return (1/12) * self.current_mass * ((self.size.x * self.size.x) + (self.size.y * self.size.y))


class Rocket(pygame.sprite.Sprite, RocketCalculation):
    def __init__(self):
        self.size = pygame.Vector2(10, 80)
        self.start_position = pygame.Vector2(200, 930)

        self.image = pygame.image.load("assets/prototype.png").convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.start_position.x, self.start_position.y))

        self.image_thrust = pygame.image.load("assets/thrust.png").convert_alpha()
        self.copy_image_thrust = self.image_thrust.copy()

        self.reset()


    def reset(self):
        self.rocket_angle = 0
        self.rocket_orientation = 0
        self.position = pygame.Vector2(self.start_position.x, self.start_position.y)
        self.test_launch_var = False
        self.direction = pygame.Vector2(0,0)

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
        self.angular_acceleration = 0
        self.angular_velocity = 0

        # 120
        self.max_thrust_power = 300 # newton
        self.current_thrust_power = 0
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)

        self.gimbal_angle = self.rocket_angle
        self.max_gimbal_angle = self.rocket_angle+2
        self.min_gimbal_angle = self.rocket_angle-2



    def controls(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_l]: # Launch go, fire rocket
            self.test_launch(dt)
   
        if keys[pygame.K_x]:
            self.current_thrust_power = self.max_thrust_power
        elif keys[pygame.K_z]:   
            self.current_thrust_power = 0

        if keys[pygame.K_d]:
            if self.gimbal_angle < self.max_gimbal_angle:
                self.gimbal_angle += 1 
        elif keys[pygame.K_a]:
            if self.gimbal_angle > self.min_gimbal_angle:
                self.gimbal_angle -= 1
        else:
            self.gimbal_angle = 0

 

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

        rotated_image_thrust = pygame.transform.rotate(self.copy_image_thrust, self.gimbal_angle+90)
        screen.blit(rotated_image_thrust, (self.rect.x, self.rect.y+self.size.y))


    def test_launch(self, dt):
        if not self.test_launch_var:
            self.reset()
            self.test_launch_var = True

            # choose angle start
            angle_start = int(input("Start angle rocket: "))
            self.rocket_angle = angle_start

            time.sleep(3)

            self.start_time = pygame.time.get_ticks()


        # calculate time thrust applied, if >= 1, thrust to 0 and free-fall rocket
        time_thrust_applied = round(((pygame.time.get_ticks() - self.start_time)//2)/1000)
        self.current_thrust_power = self.max_thrust_power
        if time_thrust_applied >= 1:
            self.current_thrust_power = 0
        print(self.current_thrust_power, time_thrust_applied, self.rocket_angle)

        self.calculate_state(dt)

        # this is just a temporary function, implement better later


# TODO: Create info rocket, tell everything about the rocket
# TODO: Create env.info(), tell everything about the environment (screenshot phone)
# TODO: Implement gradually increase of thrust (LATER)
# TODO: Upgrade graphics
# TODO: Make choice for adding mass changes/drag/gravity
# TODO: Create auto landing