import pygame
from pygame.locals import *
from pygame.sprite import Sprite, Group

pygame.init()

square_size = 120
width = square_size * 8
height = square_size * 8

screen = pygame.display.set_mode((width, height))

light_square_color = '#7D955C'
dark_square_color = '#EEEFD4'

# Draw Squares
square_list = []
for i in range(8):
    for j in range(8):
        square_surf = pygame.Surface((square_size, square_size))
        square_rect = square_surf.get_rect(topleft = (i * square_size, j * square_size))
        if ((i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1)):
            square_surf.fill(light_square_color)
        else:
            square_surf.fill(dark_square_color)

        square_list.append((square_surf, square_rect))


def draw_board():
    for square in square_list:
        screen.blit(square[0], square[1])


clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill('gray')

    draw_board()

    clock.tick(60)
    pygame.display.update()

pygame.quit()


