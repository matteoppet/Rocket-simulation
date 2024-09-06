from pygame import sprite

def collision(sprite1, group_sprites):
    if sprite.spritecollideany(sprite1, group_sprites):
        return True