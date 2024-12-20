import pygame 
import numpy as np
from game.helpers.physics import Physics

class Rocket:
    """ This class represent all the rocket, contians the overall data and has all the stages in it
        
        To create and use a rocket, you only need to call this class and the relative methods

        Methods:
            1. __init__ = initialize each stage with each component, set up the physics too
            2. render = calls the render function of each stage
            3. update = calls the update function of each stage
            4. get_altitude = returns the altitude of the rocket
            5. get_aoa = returns the angle of attack of the rocket
    """
    def __init__(self, rocket_dict_config: dict, environment):
        self.stages = pygame.sprite.Group()
        self.WORLD_OFFSET = pygame.Vector2(640, 360)
        self.physics = Physics(self, environment)

        parent = None
        for stage, components in rocket_dict_config.items():
            current_stage = Stage(stage, self)
            for component, attribs in components.items():
                if "motor" in component:
                    current_stage.motor = Stage.Motor(component, current_stage, parent, attribs, current_stage.components_group, self)
                else:
                    parent = Stage.Component(component, current_stage, parent, attribs, current_stage.components_group, self)

            self.stages.add(current_stage)

    def render(self, screen):
        for stage in self.stages:
            stage.render(screen)
    
    def update(self, time_step):
        for stage in self.stages:
            stage.update(time_step)

    def controls(self):
        keys = pygame.key.get_pressed()

        motor = None
        for stage in list(reversed(self.stages.sprites())):
            if stage.attached:
                motor = stage.motor
                break

        if motor is not None:
            if keys[pygame.K_x]: motor.current_thrust_perc = 100
            elif keys[pygame.K_z]: motor.current_thrust_perc = 0

            if keys[pygame.K_a]: motor.angle = motor.angle + 15
            if keys[pygame.K_d]: motor.angle = motor.angle - 15

        if keys[pygame.K_l]: 
            for stage in list(reversed(self.stages.sprites())):
                if stage.attached:
                    stage.detatch()
                    break

    def collision(self, other_sprites_group):
        components = [component for stage in self.stages for component in stage.components_group]
        collision = pygame.sprite.groupcollide(components, other_sprites_group, False, False)

        for key in collision.keys():
            self.stages.sprites()[int(key.stage.name)-1].collision()

    def get_altitude(self, x):
        return 0 
    
    def get_aoa(self, x):
        return 0


class Stage(pygame.sprite.Sprite):
    """ This class represent each stage the rocket has, all the components and the data

        Each stage has:
            1. name (str)
            2. components (sprite.Group)
            3. motor
            4. if is attached to other stages
            5. instance of the main rocket class

        Inner Classes:
            1. Component = each component is initializated with the class Component, inside it has some variables describing the component
            2. Motor = specific class for the motor component

        Methods:
            1. __init__ = initalize the class with different attributes
            2. render = blit all the components of the stage on the screen
            3. update = update all the components position of the stage (bit more complicated)
    """
    class Component(pygame.sprite.Sprite):
        def __init__(self, name: str, stage, parent: pygame.sprite.Sprite, attribs: dict, group: pygame.sprite.Group, rocket: classmethod):
            super().__init__(group)

            self.name = name
            self.parent = parent 
            self.group = group
            self.rocket = rocket
            self.stage = stage

            self.local_offset = attribs["local_offset"]
            self.size = attribs["size"]
            self.mass = attribs["mass"]
            self.shape = attribs["shape"]

            self.angle = 0
            self.acceleration = np.array([0.0,0.0])
            self.velocity = np.array([0.0,0.0])
            self.angular_velocity = 0

            self.image = pygame.Surface(self.size, pygame.SRCALPHA)
            self.image.fill("blue")
            self.rect = self.image.get_rect(topleft=rocket.WORLD_OFFSET+self.local_offset)

            self.position = pygame.Vector2(self.rect.centerx, self.rect.centery)

        def render(self, screen):
            rotated_image = pygame.transform.rotate(self.image, -self.angle)
            rotated_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, rotated_rect)

        def update(self, motor, components, time_step, colliding):
            thrust = 0
            if motor is not None:
                thrust = motor.get_thrust()

            acceleration, angular_acceleration = self.rocket.physics.apply(components, thrust, motor, False)
            self.velocity += acceleration * time_step
            self.angular_velocity += angular_acceleration * time_step

            self.angle += self.angular_velocity
            self.position -= self.velocity
            self.rect.center = self.position

        def copy_update(self):
            offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
            offset.rotate_ip(self.parent.angle)

            self.angle = self.parent.angle
            self.position = self.parent.position + offset
            self.rect.center = self.position

    class Motor(pygame.sprite.Sprite):
        def __init__(self, name: str, stage, parent: pygame.sprite.Sprite, attribs: dict, group: pygame.sprite.Group, rocket: classmethod):
            super().__init__(group)

            self.name = name
            self.parent = parent 
            self.group = group
            self.stage = stage

            self.local_offset = attribs["local_offset"]
            self.size = attribs["size"]
            self.mass = attribs["mass"]
            self.shape = attribs["shape"]
            self.angle = 0
            self.max_thrust = attribs["thrust"]
            self.isp = attribs["isp"]
            self.max_angle_vectoring = attribs["angle_vectoring"]

            self.current_thrust_perc = 0

            self.image = pygame.Surface(self.size, pygame.SRCALPHA)
            self.image.fill("black")
            self.rect = self.image.get_rect(topleft=rocket.WORLD_OFFSET+self.local_offset)

            self.position = pygame.Vector2(self.rect.centerx, self.rect.centery)
        
        def render(self, screen):
            rotated_image = pygame.transform.rotate(self.image, -self.angle)
            rotated_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, rotated_rect)

        def copy_update(self):
            offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
            offset.rotate_ip(self.parent.angle)

            self.angle = self.parent.angle
            self.position = self.parent.position + offset
            self.rect.center = self.position

        def get_thrust(self):
            return (self.current_thrust_perc/100)*self.max_thrust

    def __init__(self, name_stage: str, rocket: classmethod):
        super().__init__()

        self.name = str(name_stage)
        self.components_group = pygame.sprite.Group()
        self.motor = None
        self.attached = True
        self.rocket = rocket

        self.colliding = False

    def render(self, screen):
        for component in self.components_group:
            component.render(screen)

    def update(self, time_step):
        if not self.colliding:
            if self.attached:
                first_stage = self.rocket.stages.sprites()[0]
                # updating only the nose of the rocket
                if self.name == first_stage.name:
                    for component in self.components_group:
                        if component.parent == None:
                            # get current motor
                            motor = None
                            for stage in reversed(list(self.rocket.stages.sprites())):
                                if stage.attached:
                                    motor = stage.motor
                                    break
            
                            # get all the component
                            components = []
                            nose = None
                            for stage in self.rocket.stages:
                                for component in stage.components_group:
                                    components.append(component)
                                    if component.name == "nose": nose = component
                            nose.update(motor, components, time_step, self.colliding)

                        # copy the parent position for each component
                        else:
                            for component in self.components_group:
                                if component.parent != None:
                                    component.copy_update()
                # update position of the current stage based on the parent position (the first one will be of the previous stage)
                else: 
                    for component in self.components_group:
                        component.copy_update()
            else:
                # loop throught the component, the first component will update itself, the other components below it will follow their parent
                for component in self.components_group.sprites():
                    if component.name == self.components_group.sprites()[0].name:
                        component.update(self.motor, self.components_group.sprites(), time_step, self.colliding)
                    else:
                        component.copy_update()

    def detatch(self):
        self.attached = False
        self.motor.current_thrust_perc = 0

    def collision(self):
        if self.attached:  
            for stage in self.rocket.stages:
                stage.colliding = True
        else:
            self.colliding = True

# motor not working in the new stage
# there is a problem when rotating to the left, probably is the mass distribution and the CP or CG position (the x component)