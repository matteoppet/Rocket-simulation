import pygame 
from settings import *
import math
import time

class RocketCalculation:
    EXPONENTIAL_DECAY_CONSTANT = 0.02 # search docs rockets engines

    def calculate_state(self, dt):
        if self.get_weight.y > self.max_thrust_power:
            print("ERROR: Thrust power too lower for the weight of the rocket")
        self.thrust_vector = pygame.Vector2(0, self.current_thrust_power)


        self.calculate_acceleration()
        self.calculate_velocity(dt)
        self.calculate_angular_acceleration()
        self.calculate_angular_velocity(dt)

        self.calculate_drag()

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

        print(self.get_resultance_force)

        self.acceleration = self.get_resultance_force/self.mass
    
    def calculate_velocity(self, dt):
        self.velocity += self.acceleration * dt

    def calculate_angular_acceleration(self): # returns radians
        self.angular_acceleration = self.get_torque / self.get_inertia

    def calculate_angular_velocity(self, dt):
        self.angular_velocity = self.angular_acceleration * dt

    def calculate_drag(self):
        air_density = self.get_air_density
        rocket_velocity = self.velocity.length()

        drag_magnitude = 0.5 * air_density * (rocket_velocity**2) * DRAG_COEFF * self.get_cross_sectional_area
        
        if self.velocity.magnitude() != 0: drag_direction = self.velocity.normalize()
        else: drag_direction = pygame.Vector2(0, 0)

        drag_vector = drag_direction * drag_magnitude
        
        return drag_vector


    @property
    def get_weight(self): # return newton (weight(kg) * gravity)
        return pygame.Vector2(0, self.mass * GRAVITY)
    @property
    def get_resultance_force(self): # return newton (thrustx-weight
        return self.thrust_vector - self.get_weight - self.calculate_drag()
    @property
    def get_torque(self):
        return self.current_thrust_power * 40 * math.sin(self.gimbal_angle)
    @property
    def get_inertia(self):
        return (1/12) * self.current_mass * ((self.size.x * self.size.x) + (self.size.y * self.size.y))
    @property
    def get_cross_sectional_area(self):
        angle_in_radians = math.radians(self.rocket_angle)
        return abs(self.size.x * math.cos(angle_in_radians)) + abs(self.size.y * math.sin(angle_in_radians))
    @property
    def get_air_density(self):
        # temperature = 15 degrees
        # pressure = 1013.15 hpa
        # air density sea level = 1.225
        return 1.225 * (1-(self.get_altitude/100000)*2)
    @property
    def get_altitude(self):
        return WINDOW_HEIGHT-30 - self.rect.bottomleft[1]



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
        self.max_thrust_power = 200 # newton
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


    def test_launch(self, dt): # TODO: Set up better
        if not self.test_launch_var:
            self.reset()
            self.test_launch_var = True

            # choose angle start
            angle_start = int(input("Start angle rocket: "))
            self.rocket_angle = angle_start
            self.gimbal_angle = self.rocket_angle

            self.info()
            fire = int(input("Fire (0-1): "))

            if fire == 1:
                time.sleep(3)
                print()
                self.start_time = pygame.time.get_ticks()

                # calculate time thrust applied, if >= 1, thrust to 0 and free-fall rocket
                time_thrust_applied = round(((pygame.time.get_ticks() - self.start_time)//2)/1000)
                self.current_thrust_power = self.max_thrust_power
                if time_thrust_applied >= 1:
                    self.current_thrust_power = 0
                print(self.current_thrust_power, time_thrust_applied, self.rocket_angle)

                self.calculate_state(dt)
            else:
                self.test_launch_var = False
                self.reset()

        # this is just a temporary function, implement better later


    def info(self): # TODO: Set up better
        # initial mass
        print("\nInitial mass: ", self.mass)
        # initial fuel
        print("Initial fuel: ", self.fuel)
        # rocket angle start
        print("Starting angle rocket: ", self.rocket_angle)
        # radius thrust
        print("Radius thrust: ", self.radius_thrust)
        # reference area
        print("Reference area: ", self.reference_area)
        # max_thrust_power
        print("\nEngine thrust power: ", self.max_thrust_power)
        # gimbal start angle
        print("Engine start angle: ", self.gimbal_angle)



# TODO: Create info rocket, tell everything about the rocket (DONE, FINISH LATER BETTER)
# TODO: Create env.info(), tell everything about the environment (screenshot phone)
# TODO: Implement gradually increase of thrust (LATER)
# TODO: Upgrade graphics
# TODO: Make choice for adding mass changes/drag/gravity
# TODO: Create auto landing
# TODO: Create trajectory line each step the rocket takes (not predict)

# drag coeff 0.1 to 1.9
# speed bug