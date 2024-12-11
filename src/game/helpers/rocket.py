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

    def update(self, physics: classmethod, time_step: int, colliding: dict):
        if not colliding:
            if self.is_attached:
                if self.parent:
                    offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
                    offset.rotate_ip(self.parent.angle)

                    self.angle = self.parent.angle
                    self.position = self.parent.position + offset
                else:
                    components = []
                    for component in self.group:
                        if component.is_attached:
                            components.append(component)
                        else:
                            break
                    acceleration, angular_acceleration = physics.apply(components)
                    self.velocity += acceleration * time_step
                    self.angular_velocity += angular_acceleration * time_step

                    self.position -= self.velocity
                    self.angle += self.angular_velocity
            else:
                try: 
                    acceleration, angular_acceleration = physics.apply(self.detached_sprites_group_list)
                except AttributeError:
                    acceleration, angular_acceleration = physics.apply([self])

                self.velocity += acceleration * time_step
                self.angular_velocity += angular_acceleration * time_step

                self.angle += self.angular_velocity
                self.position -= self.velocity
        else:
            ...

        self.rect.center = self.position

    def detatch(self):
        """ 
            when a component is detatched, it will create a group for all the components below it, 
            it will iterate in a reversed list of the old group of all sprites, (from bottom to top), it will add everything to the new group and stop when it encounter the not attached component,
            and it will copy the velocity from the nose.
        """
        self.detached_sprites_group = pygame.sprite.Group()
        self.is_attached = False

        for sprite in list(reversed(self.group.sprites())):
            if sprite.is_attached:
                self.detached_sprites_group.add(sprite)
            else:
                self.detached_sprites_group.add(sprite)
                break

        self.detached_sprites_group_list = list(reversed(self.detached_sprites_group.sprites()))

        first_command_sprite = self.detached_sprites_group_list[0].name
        for sprite in self.detached_sprites_group_list:
            if sprite.name != self.detached_sprites_group_list[0].name:
                sprite.command_parent = first_command_sprite

        self.velocity = self.group.sprites()[0].velocity.copy()
        self.angular_velocity = self.group.sprites()[0].angular_velocity

class Motor(pygame.sprite.Sprite):
    def __init__(self, name, parent, command_parent, attribs, group):
        super().__init__(group)
        
        self.name = name
        self.parent = parent
        self.command_parent = command_parent
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

    def update(self, a, b, c):
        offset = pygame.math.Vector2(0, self.size.y // 2 + self.parent.size.y // 2)
        offset.rotate_ip(self.parent.angle)

        self.angle = self.parent.angle
        self.position = self.parent.position + offset
        self.rect.center = self.position

    @property
    def get_thrust(self):
        return (self.current_thrust_perc/100)*self.max_thrust

class Rocket:
    def __init__(self, components, environment):
        self.components = components
        self.components_sprite_group = pygame.sprite.Group()
        self.motor_sprite_group = pygame.sprite.Group() 

        parent = None
        for component, attribs in self.components.items():
            if component == "motor":
                Motor(component, parent, attribs, [self.components_sprite_group, self.motor_sprite_group])
            else:
                parent = Component(component, parent, attribs, self.components_sprite_group)

        # TODO: TEMPORARY, implement better activation motor
        self.motor_sprite_group.sprites()[-1].active = True

        self.environment = environment
        self.physics = Physics(self, self.environment)

        self.count = 0
            
    def render(self, screen):
        for component in self.components_sprite_group:
            component.render(screen)

    def update(self, time_step, other_sprites: pygame.sprite.Group):
        for component in self.components_sprite_group:
            # call collision function (if detached_sprites_group is available, use it, instead, use the original group)
            try: colliding = self.collision(other_sprites, component.detached_sprites_group)
            except AttributeError: colliding = self.collision(other_sprites, self.components_sprite_group)

            component.update(self.physics, time_step, colliding)

    def collision(self, other_sprites: pygame.sprite.Group, group_component: pygame.sprite.Group):
        collision = pygame.sprite.groupcollide(group_component, other_sprites, False, False)
        if collision:
            return True
        
    def controls(self):
        keys = pygame.key.get_pressed()

        active_motor = None
        for motor in self.motor_sprite_group:
            if motor.active: active_motor = motor

        if keys[pygame.K_x]: active_motor.current_thrust_perc = 100
        elif keys[pygame.K_z]: active_motor.current_thrust_perc = 0

        if keys[pygame.K_a]: active_motor.angle = active_motor.angle + 15
        elif keys[pygame.K_d]: active_motor.angle = active_motor.angle - 15

        if keys[pygame.K_l]:
            component = self.components_sprite_group.sprites()[-2]

            if component.is_attached:
                component.detatch()
            
    def get_altitude(self, center_component_y):
        return self.environment.base_terrain.y - center_component_y
    
    def get_aoa(self, component):
        return abs(self.environment.get_wind_angle - component.angle) 