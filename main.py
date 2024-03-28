import pygame
from pygame.locals import *
from pygame.sprite import Sprite, Group
import math

pygame.init()

square_size = 127
width = square_size * 8
height = square_size * 8

screen = pygame.display.set_mode((width, height))

light_square_color = '#7D955C'
dark_square_color = '#EEEFD4'

# Draw Squares
square_list = [[None for _ in range(8)] for _ in range(8)]
pieces_pos_list = [[None for _ in range(8)] for _ in range(8)]
square_centers = []
pieces_list = []

for i in range(8):
    for j in range(8):
        square_surf = pygame.Surface((square_size, square_size))
        square_rect = square_surf.get_rect(topleft = (i * square_size, j * square_size))
        square_centers.append(square_rect.center)
        if ((i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1)):
            square_surf.fill(light_square_color)
        else:
            square_surf.fill(dark_square_color)

        square_list[i][j] = (square_surf, square_rect)


class Piece:
    picked = None

    def __init__(self, image_location, position):
        self.surf = pygame.image.load(image_location).convert_alpha()
        self.rect = self.surf.get_rect(topleft=(position[0] * square_size, position[1] * square_size))
        self.position = position
        pieces_pos_list[position[0]][position[1]] = self
        pieces_list.append(self)


# Initializing Chess Pieces with default positions
w_king = Piece('Chess/graphics/Chess-pieces/white-king.png', (4, 7))
w_queen = Piece('Chess/graphics/Chess-pieces/white-queen.png', (3, 7))
w_rook1 = Piece('Chess/graphics/Chess-pieces/white-rook.png', (0, 7))
w_bishop1 = Piece('Chess/graphics/Chess-pieces/white-bishop.png', (2, 7))
w_knight1 = Piece('Chess/graphics/Chess-pieces/white-knight.png', (1, 7))
w_rook2 = Piece('Chess/graphics/Chess-pieces/white-rook.png', (7, 7))
w_bishop2 = Piece('Chess/graphics/Chess-pieces/white-bishop.png', (5, 7))
w_knight2 = Piece('Chess/graphics/Chess-pieces/white-knight.png', (6, 7))
w_pawn1 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (0, 6))
w_pawn2 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (1, 6))
w_pawn3 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (2, 6))
w_pawn4 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (3, 6))
w_pawn5 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (4, 6))
w_pawn6 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (5, 6))
w_pawn7 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (6, 6))
w_pawn8 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (7, 6))

b_king = Piece('Chess/graphics/Chess-pieces/black-king.png', (4, 0))
b_queen = Piece('Chess/graphics/Chess-pieces/black-queen.png', (3, 0))
b_rook1 = Piece('Chess/graphics/Chess-pieces/black-rook.png', (0, 0))
b_bishop1 = Piece('Chess/graphics/Chess-pieces/black-bishop.png', (2, 0))
b_knight1 = Piece('Chess/graphics/Chess-pieces/black-knight.png', (1, 0))
b_rook2 = Piece('Chess/graphics/Chess-pieces/black-rook.png', (7, 0))
b_bishop2 = Piece('Chess/graphics/Chess-pieces/black-bishop.png', (5, 0))
b_knight2 = Piece('Chess/graphics/Chess-pieces/black-knight.png', (6, 0))
b_pawn1 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (0, 1))
b_pawn2 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (1, 1))
b_pawn3 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (2, 1))
b_pawn4 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (3, 1))
b_pawn5 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (4, 1))
b_pawn6 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (5, 1))
b_pawn7 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (6, 1))
b_pawn8 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (7, 1))


def closest_point(point, points):
    min_distance = float('inf')
    closest = None
    
    for p in points:
        distance = math.sqrt((point[0] - p[0])**2 + (point[1] - p[1])**2)
        if distance < min_distance:
            min_distance = distance
            closest = p
    
    return closest


def draw_board():
    for i in range(8):
        for j in range(8):
            square = square_list[i][j]
            screen.blit(square[0], square[1])

    for piece in pieces_list:
        screen.blit(piece.surf, piece.rect)


clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                for piece in pieces_list:
                    if piece.rect.collidepoint(event.pos): 
                        Piece.picked = piece
                        pieces_list.remove(piece)
                        pieces_list.append(piece)
                        break
            
        if event.type == MOUSEMOTION:
            if Piece.picked:
                Piece.picked.rect.center = event.pos

        if event.type == MOUSEBUTTONUP:
            if Piece.picked:
                Piece.picked.rect.center = closest_point(Piece.picked.rect.center, square_centers)
                Piece.picked = None

    screen.fill('gray')

    draw_board()

    clock.tick(60)
    pygame.display.update()

pygame.quit()


