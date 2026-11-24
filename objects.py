import pygame
class Square:
    def __init__(self, x, y, size, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

def load_player(image_path):
    image = pygame.image.load(image_path)
    rect = image.get_rect()
    rect.topleft = (100, 100)
    return image, rect# Escribe tu código aquí :-)
