import pygame 
from settings import *

class RocketCalculation:
    EXPONENTIAL_DECAY_CONSTANT = 0.02 # search docs rockets engines

    def calculate_state(self, dt):
        # check parts
        if self.get_weight.y > self.max_thrust_power:
            print("ERROR: Thrust power too lower for the weight of the rocket")
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power).rotate(self.current_gimbal_angle)

        self.calculate_acceleration()
        self.calculate_velocity(dt)

        self.calculate_angular_acceleration()
        self.calculate_angular_velocity(dt)

        self.rocket_angle += self.angular_velocity * dt

        print(self.rocket_angle)

        self.position -= self.velocity


    def calculate_acceleration(self):
        self.acceleration = self.get_resultance_force/self.mass
    
    def calculate_velocity(self, dt):
        self.velocity += self.acceleration * dt
    
    def calculate_angular_acceleration(self):
        ...

    def calculate_angular_velocity(self, dt):
        ...


    @property
    def get_weight(self): # return newton (weight(kg) * gravity)
        return pygame.Vector2(0, self.mass * GRAVITY)
    @property
    def get_resultance_force(self): # return newton (thrust-weight)
        return self.thrust_vector - self.get_weight
    @property
    def get_angle_rocket(self):
        return self.thrust_vector.angle_to(self.vertical_vector)
    @property
    def get_torque(self):
        return self.thrust_vector.y * (self.size.y/2)
    @property
    def get_inertia(self):
        return 5416.67


class Rocket(pygame.sprite.Sprite, RocketCalculation):
    def __init__(self):
        self.size = pygame.Vector2(10, 80)
        self.start_position = pygame.Vector2(200, 800)

        self.image = pygame.image.load("assets/prototype.png").convert_alpha()
        self.copy_image = self.image.copy()
        self.rect = self.image.get_rect(center=(self.start_position.x, self.start_position.y))

        self.reset()


    def reset(self):
        self.legs = True
        self.rocket_angle = 0
        self.position = pygame.Vector2(self.start_position.x, self.start_position.y)


        self.mass = 10
        self.fuel = 1000.0
        self.current_mass = self.mass
        self.current_fuel = self.fuel
        # self.inertia = self.get_inertia
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

        self.max_thrust_power = 120 # newton
        self.current_thrust_power = 0
        self.gimbal_limit = 20
        self.current_gimbal_angle = 0
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)

        self.vertical_vector = (0, -1)


    def controls(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_x]:
            self.current_thrust_power = self.max_thrust_power
        elif keys[pygame.K_z]:
            self.current_thrust_power = 0

        if keys[pygame.K_d]:
            if self.current_gimbal_angle >= self.gimbal_limit:
                self.current_gimbal_angle = self.gimbal_limit
            else:
                self.current_gimbal_angle += self.gimbal_limit
        if keys[pygame.K_a]:
            if self.current_gimbal_angle < -self.gimbal_limit:
                self.current_gimbal_angle = -self.gimbal_limit
            else:
                self.current_gimbal_angle -= self.gimbal_limit
 


    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.copy_image, self.rocket_angle)
        screen.blit(rotated_image, self.position)
    


# acceration (no drag, no mass changed) DONE
# velocity based on acceleration DONE

# implement rocket simulation graphic (and rotate it) (AFTER)
# angular velocity (i.e. the rocket continues to rotate if the gimbal rocket is always to the right) 
# rotate the thrust based on the angle of the gimbal rocket
# rotate the rocket based on the angle of which is pointed the rocket

# angle thrust rocket and change horizontal acc and vel 

# make choice do add gravity and mass changes
# acceleration (with drag and mass changes)