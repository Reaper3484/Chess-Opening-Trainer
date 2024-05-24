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


class Board:
    def __init__(self):
        self.square_list = [[None for _ in range(8)] for _ in range(8)]
        self.pieces_pos_list = [[None for _ in range(8)] for _ in range(8)]
        self.square_centers = []
        self.pieces_list = []
        self.initialise_board()

    def initialise_board(self):
        for i in range(8):
            for j in range(8):
                square_surf = pygame.Surface((square_size, square_size))
                square_rect = square_surf.get_rect(topleft = (i * square_size, j * square_size))
                self.square_centers.append(square_rect.center)
                if ((i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1)):
                    square_surf.fill(light_square_color)
                else:
                    square_surf.fill(dark_square_color)

                self.square_list[i][j] = (square_surf, square_rect)

    def closest_point(self, point, points):
        min_distance = float('inf')
        closest = None
        
        for p in points:
            distance = math.sqrt((point[0] - p[0])**2 + (point[1] - p[1])**2)
            if distance < min_distance:
                min_distance = distance
                closest = p
        
        return closest

    def draw_board(self):
        for i in range(8):
            for j in range(8):
                square = self.square_list[i][j]
                screen.blit(square[0], square[1])

        for piece in self.pieces_list:
            piece.display()
    

class Piece:
    picked = None

    def __init__(self, image_location, position, id):
        self.surf = pygame.image.load(image_location).convert_alpha()
        self.rect = self.surf.get_rect(topleft=(position[0] * square_size, position[1] * square_size))
        self.id = id
        self.position = position
        board.pieces_pos_list[position[0]][position[1]] = self
        board.pieces_list.append(self)
        self.update_position(self.position)

    def update_position(self, position):
        self.position = position
        if self.position:
            self.rect.topleft = (self.position[0] * square_size, self.position[1] * square_size)
            self.rect.center = board.closest_point(self.rect.center, board.square_centers)
        else:
            self.rect.topleft = (-500, -500)

    def get_postion(self):
        return self.position

    def display(self):
        screen.blit(self.surf, self.rect)


# Initializing Board and Chess Pieces with default positions
board = Board()
w_king = Piece('Chess/graphics/Chess-pieces/white-king.png', (4, 7), 'K')
w_queen = Piece('Chess/graphics/Chess-pieces/white-queen.png', (3, 7), 'Q')
w_rook1 = Piece('Chess/graphics/Chess-pieces/white-rook.png', (0, 7), 'R')
w_bishop1 = Piece('Chess/graphics/Chess-pieces/white-bishop.png', (2, 7), 'B')
w_knight1 = Piece('Chess/graphics/Chess-pieces/white-knight.png', (1, 7), 'N')
w_rook2 = Piece('Chess/graphics/Chess-pieces/white-rook.png', (7, 7), 'R')
w_bishop2 = Piece('Chess/graphics/Chess-pieces/white-bishop.png', (5, 7), 'B')
w_knight2 = Piece('Chess/graphics/Chess-pieces/white-knight.png', (6, 7), 'N')
w_pawn1 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (0, 6), 'P')
w_pawn2 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (1, 6), 'P')
w_pawn3 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (2, 6), 'P')
w_pawn4 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (3, 6), 'P')
w_pawn5 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (4, 6), 'P')
w_pawn6 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (5, 6), 'P')
w_pawn7 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (6, 6), 'P')
w_pawn8 = Piece('Chess/graphics/Chess-pieces/white-pawn.png', (7, 6), 'P')

b_king = Piece('Chess/graphics/Chess-pieces/black-king.png', (4, 0), 'k')
b_queen = Piece('Chess/graphics/Chess-pieces/black-queen.png', (3, 0), 'q')
b_rook1 = Piece('Chess/graphics/Chess-pieces/black-rook.png', (0, 0), 'r')
b_bishop1 = Piece('Chess/graphics/Chess-pieces/black-bishop.png', (2, 0), 'b')
b_knight1 = Piece('Chess/graphics/Chess-pieces/black-knight.png', (1, 0), 'n')
b_rook2 = Piece('Chess/graphics/Chess-pieces/black-rook.png', (7, 0), 'r')
b_bishop2 = Piece('Chess/graphics/Chess-pieces/black-bishop.png', (5, 0), 'b')
b_knight2 = Piece('Chess/graphics/Chess-pieces/black-knight.png', (6, 0), 'n')
b_pawn1 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (0, 1), 'p')
b_pawn2 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (1, 1), 'p')
b_pawn3 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (2, 1), 'p')
b_pawn4 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (3, 1), 'p')
b_pawn5 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (4, 1), 'p')
b_pawn6 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (5, 1), 'p')
b_pawn7 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (6, 1), 'p')
b_pawn8 = Piece('Chess/graphics/Chess-pieces/black-pawn.png', (7, 1), 'p')


def import_fen(fen_string):
    rank = 0
    file = 0
    repeat = {
        'r': 0,
        'n': 0,
        'b': 0,
        'p': 0,
        'R': 0,
        'N': 0,
        'B': 0,
        'P': 0,
    }

    for piece in board.pieces_list:
        piece.update_position(None) 

    for c in fen_string:
        if (c.isnumeric() and 1 < int(c) < 9):
            file += int(c)
            continue

        elif (c == '/'):
            file = 0
            rank += 1
            continue

        match c:
            case 'r':
                if (repeat[c] == 0):
                    b_rook1.update_position((file, rank))
                    repeat[c] = 1
                else:
                    b_rook2.update_position((file, rank))
            
            case 'n':
                if (repeat[c] == 0):
                    b_knight1.update_position((file, rank))
                    repeat[c] = 1
                else:
                    b_knight2.update_position((file, rank))

            case 'b':
                if (repeat[c] == 0):
                    b_bishop1.update_position((file, rank))
                    repeat[c] = 1
                else:
                    b_bishop2.update_position((file, rank))
            
            case 'q':
                b_queen.update_position((file, rank))

            case 'k':
                b_king.update_position((file, rank))

            case 'p':
                if (repeat[c] == 0):
                    b_pawn1.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 1):
                    b_pawn2.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 2):
                    b_pawn3.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 3):
                    b_pawn4.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 4):
                    b_pawn5.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 5):
                    b_pawn6.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 6):
                    b_pawn7.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 7):
                    b_pawn8.update_position((file, rank))
                    repeat[c] += 1
            
            case 'R':
                if (repeat[c] == 0):
                    w_rook1.update_position((file, rank))
                    repeat[c] = 1
                else:
                    w_rook2.update_position((file, rank))

            case 'N':
                if (repeat[c] == 0):
                    w_knight1.update_position((file, rank))
                    repeat[c] = 1
                else:
                    w_knight2.update_position((file, rank))

            case 'B':
                if (repeat[c] == 0):
                    w_bishop1.update_position((file, rank))
                    repeat[c] = 1
                else:
                    w_bishop2.update_position((file, rank))
            
            case 'Q':
                w_queen.update_position((file, rank))

            case 'K':
                w_king.update_position((file, rank))

            case 'P':
                if (repeat[c] == 0):
                    w_pawn1.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 1):
                    w_pawn2.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 2):
                    w_pawn3.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 3):
                    w_pawn4.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 4):
                    w_pawn5.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 5):
                    w_pawn6.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 6):
                    w_pawn7.update_position((file, rank))
                    repeat[c] += 1
                elif (repeat[c] == 7):
                    w_pawn8.update_position((file, rank))
                    repeat[c] += 1
        
        file += 1


import_fen('rnbqkbnr/pppppppp/////PPPPPPPP/RNBQKBNR')

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                for piece in board.pieces_list:
                    if piece.rect.collidepoint(event.pos): 
                        Piece.picked = piece
                        board.pieces_list.remove(piece)
                        board.pieces_list.append(piece)
                        break
            
        if event.type == MOUSEMOTION:
            if Piece.picked:
                Piece.picked.rect.center = event.pos

        if event.type == MOUSEBUTTONUP:
            if Piece.picked:
                index = board.square_centers.index(board.closest_point(Piece.picked.rect.center, board.square_centers))
                Piece.picked.update_position((index // 8, index % 8))
                for piece in board.pieces_list:
                    if piece != Piece.picked and piece.rect.center == Piece.picked.rect.center:
                        piece.update_position(None)
                        break

                Piece.picked = None

    screen.fill('gray')

    board.draw_board()

    clock.tick(60)
    pygame.display.update()

pygame.quit()


