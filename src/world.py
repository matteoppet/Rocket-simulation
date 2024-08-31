from pygame import sprite, Rect, Surface

class Floor(sprite.Sprite):
    def __init__(self, window_width, window_height):
        self.width = window_width
        self.height = window_height/4
        self.color = "black"

        self.x = 0
        self.y = window_height-self.height

        self.image = Surface((self.width, self.height))
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.image.fill(self.color)


    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))