import pygame
import numpy as np
from game.helpers.physics import Physics

WORLD_OFFSET = pygame.Vector2(640, 360)

class Component(pygame.sprite.Sprite):
    def __init__(self, name: str, parent: pygame.sprite.Sprite, attribs: dict, group: pygame.sprite.Group):
        super().__init__(group)

        self.name = name
        self.parent = parent
        self.child = None
        self.group = group

        self.local_offset = attribs["local_offset"]
        self.size = attribs["size"]
        self.mass = attribs["mass"]
        self.shape = attribs["shape"]

        self.is_attached = True
        self.angle = 0
        self.acceleration = np.array([0.0, 0.0])
        self.velocity = np.array([0.0, 0.0])
        self.angular_velocity = 0

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill("blue")
        self.rect = self.image.get_rect(topleft=WORLD_OFFSET+self.local_offset)

        self.position = pygame.Vector2(self.rect.center[0], self.rect.center[1])

    def render(self, screen: pygame.Surface):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect)

    def update(self, physics: classmethod, time_step: int, colliding: bool, rocket, motor_group):
        # if its not colliding, move the component else stop moving
        if self.is_attached:
            # if its attached and has a parent, follow the parent else, move itself
            if self.parent:
                self.copy_position()
            else:
                components = []
                for stage in rocket:
                    if stage[1] == True:
                        for sprite in stage[0]:
                            components.append(sprite)
                self.update_position(physics, components, time_step, colliding, motor_group)
        else:
            self.update_position(physics, self.group.sprites(), time_step, colliding, motor_group)

        self.rect.center = self.position

    
    def update_position(self, physics, group, time_step, colliding, motor_group):
        thrust = 0
        for motor in reversed(list(motor_group)):
            if motor.active:
                thrust = motor.get_thrust

        acceleration, angular_acceleration = physics.apply(group, thrust, motor, colliding)

        if colliding:
            self.velocity = np.array([0.0, 0.0])

        self.velocity += acceleration * time_step
        self.angular_velocity += angular_acceleration * time_step

        self.angle += self.angular_velocity
        self.position -= self.velocity


    def copy_position(self):
        offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
        offset.rotate_ip(self.parent.angle)

        self.angle = self.parent.angle
        self.position = self.parent.position + offset


    def detatch(self, first_stage):
        """ 
            when a component is detatched, it will create a group for all the components below it, 
            it will iterate in a reversed list of the old group of all sprites, (from bottom to top), it will add everything to the new group and stop when it encounter the not attached component,
            and it will copy the velocity from the nose.
        """
        self.is_attached = False

        for component in self.group:
            if component.name == "motor":
                component.deactivate()

        self.velocity = first_stage.sprites()[0].velocity.copy()
        self.angular_velocity = first_stage.sprites()[0].angular_velocity

class Motor(pygame.sprite.Sprite):
    def __init__(self, name, parent, attribs, group):
        super().__init__(group)
        
        self.name = name
        self.parent = parent
        self.group = group

        self.local_offset = attribs["local_offset"]
        self.size = attribs["size"]
        self.mass = attribs["mass"]
        self.shape = attribs["shape"]

        self.is_attached = True
        self.active = False
        self.angle = 0
        self.max_angle_vectoring = attribs["angle_vectoring"]
        self.max_thrust = attribs["thrust"]
        self.isp = attribs["isp"]

        self.angular_velocity = 0

        self.current_thrust_perc = 0

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill("black")
        self.rect = self.image.get_rect(topleft=WORLD_OFFSET+self.local_offset)

        self.position = pygame.Vector2(self.rect.centerx, self.rect.centery)

    def render(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rotated_rect)

    def update(self, *args):
        offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
        offset.rotate_ip(self.parent.angle)

        self.angle = self.parent.angle
        self.position = self.parent.position + offset
        self.rect.center = self.position

    def deactivate(self):
        self.current_thrust_perc = 0

    @property
    def get_thrust(self):
        return (self.current_thrust_perc/100)*self.max_thrust

class Rocket:
    def __init__(self, components, environment):
        self.components = components
        self.motor_sprite_group = pygame.sprite.Group() 

        self.groups_stages = []
        parent = None
        for stage, components in self.components.items():
            stage_group = pygame.sprite.Group()
            for component, attribs in components.items():
                if component == "motor":
                    Motor(component, parent, attribs, [stage_group, self.motor_sprite_group])
                else:
                    parent = Component(component, parent, attribs, stage_group)

            self.groups_stages.append([stage_group, True])

        self.environment = environment
        self.physics = Physics(self, self.environment)

        self.count = 0

    def render(self, screen):
        for group in self.groups_stages:
            for sprite in group[0]:
                sprite.render(screen)

    def update(self, time_step, other_sprites: pygame.sprite.Group):
        for group in self.groups_stages:
            colliding = self.collision(group[0], other_sprites)
            group[0].update(self.physics, time_step, colliding, self.groups_stages, self.motor_sprite_group)

    def collision(self, other_sprites: pygame.sprite.Group, group_component: pygame.sprite.Group):
        collision = pygame.sprite.groupcollide(group_component, other_sprites, False, False)
        if collision:
            return True
        return False

    def controls(self):
        keys = pygame.key.get_pressed()

        active_motor = None
        for group in list(reversed(self.groups_stages)):
            if group[1] == True:
                for sprite in list(reversed(group[0].sprites())):
                    if sprite.name == "motor":
                        active_motor = sprite
                        sprite.active = True

        if active_motor:
            if keys[pygame.K_x]: active_motor.current_thrust_perc = 100
            elif keys[pygame.K_z]: active_motor.current_thrust_perc = 0

            if keys[pygame.K_a]: active_motor.angle = active_motor.angle + 15
            elif keys[pygame.K_d]: active_motor.angle = active_motor.angle - 15

        if keys[pygame.K_l]:
            for stage in list(reversed(self.groups_stages)):
                if stage[1] == True:
                    separated_stage = stage[0]
                    first_stage = self.groups_stages[0]
                    stage[1] = False
                    break
            
            try:
                for component in separated_stage:
                    if component.name != "motor":
                        component.detatch(first_stage[0])
            except UnboundLocalError:
                pass

            
    def get_altitude(self, center_component_y):
        return self.environment.base_terrain.y - center_component_y
    
    def get_aoa(self, component):
        return abs(self.environment.get_wind_angle - component.angle) 
    