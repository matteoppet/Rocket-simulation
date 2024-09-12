from pygame import sprite, Surface, transform
from python_scripts.environment import Environment


class Earth(sprite.Sprite, Environment):
    def __init__(self, window_size, group):
        sprite.Sprite.__init__(self)
        super().__init__(group)

        Environment.__init__(
            self,
            name="earth",
            gravity=9.81,
            drag_coeff=0.1,
            air_density_sea_level=1.225,
            beginning_of_space=100000
        )

        self.starting_position = (0,80)
        self.size = (window_size[0], window_size[1]/2)
        self.color = "dark green"

        self.count = 2
        self.init_stack_terrain()
