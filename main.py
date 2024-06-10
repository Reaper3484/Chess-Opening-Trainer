import pygame
from pygame.locals import *
from pygame.sprite import Sprite, Group
import math
import json

pygame.init()

square_size = 127
width = square_size * 8 + (square_size * 4)
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
        self.moves_list = []
        self.move_number = 0
        self.can_move = True
        self.user_colour = 'white'
        self.colour_to_move = 'white'
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

    def get_position(self):
        return self.position

    def display(self):
        screen.blit(self.surf, self.rect)


class UI:
    def __init__(self):
        font = pygame.font.Font(None, 90)
        self.train_text_surf = font.render('Train', True, '#231f20')
        self.train_text_rect = self.train_text_surf.get_rect(topleft=(9 * square_size, 4 * square_size + square_size/16))

        self.learn_text_surf = font.render('Learn', True, '#231f20')
        self.learn_text_rect = self.learn_text_surf.get_rect(topleft=(9 * square_size, 5 * square_size + square_size/16))

        self.image = pygame.image.load('graphics/flip_icon.png').convert_alpha()
        self.flip_button_surf = pygame.transform.scale(self.image, (square_size - 40, square_size - 40))
        self.flip_button_rect = self.flip_button_surf.get_rect(center=(9 * square_size + self.learn_text_rect.size[0]//2, 6 * square_size + square_size/16))

        self.can_press_learn = True

    def draw(self):
        pygame.draw.rect(screen, 'white', self.train_text_rect, border_radius=5)
        screen.blit(self.train_text_surf, self.train_text_rect)

        if self.can_press_learn:
            pygame.draw.rect(screen, 'white', self.learn_text_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, 'dark grey', self.learn_text_rect, border_radius=5)
        screen.blit(self.learn_text_surf, self.learn_text_rect)

        pygame.draw.rect(screen, 'white', self.flip_button_rect, border_radius=5)
        screen.blit(self.flip_button_surf, self.flip_button_rect)

    def refresh(self):
        if board.user_colour == 'white' and board.colour_to_move == 'white':
            self.can_press_learn = True
        elif board.user_colour == 'black' and board.colour_to_move == 'black':
            self.can_press_learn = True
        else:
            self.can_press_learn = False

    def train(self):
        with open('data.json', 'r') as file:
            ai.data = json.load(file)

        ai.is_training = True
        ai.move()

    def flip(self):
        board.user_colour = 'white' if board.user_colour == 'black' else 'black'
        fen = ''
        old_fen = generate_fen()
        for c in old_fen[:-3]:
            fen = c + fen
        fen += old_fen[-2:]
        
        import_fen(fen)
        ui.refresh()

    def learn(self):
        if not ai.is_learning:
            ai.is_learning = True
            if board.user_colour == 'white':
                ai.start_move = board.move_number + 1

            with open('data.json', 'r') as file:
                ai.data = json.load(file)

        else:
            ai.is_learning = False
            ai.end_move = board.move_number
            ai.learn()
            with open('data.json', 'w') as file:
                json.dump(ai.data, file, indent=4)


class AI:
    def __init__(self):
        self.is_learning = False
        self.is_training = False
        self.start_move = 0
        self.end_move = 0
        self.temp = ''
        self.data = {"AI as black": {},
                     "AI as white": {}}

    def move(self):
        if not ai.is_training:
            return

        if board.move_number % 2:
            fen = ai.data['AI as black'][generate_fen()]
            board.move_number += 1
            import_fen(fen)
            board.moves_list.append(fen)
            board.colour_to_move = 'black' if board.colour_to_move == 'white' else 'white'

        else:
            fen = ai.data['AI as white'][generate_fen()]
            board.move_number += 1
            import_fen(fen)
            board.moves_list.append(fen)
            board.colour_to_move = 'black' if board.colour_to_move == 'white' else 'white'

    def learn(self):
        for i in range(self.start_move, self.end_move, 2):
            if i + 1 < len(board.moves_list):
                if board.user_colour == 'white': 
                    white_move_fen = board.moves_list[i]
                    black_move_fen = board.moves_list[i + 1]
                    ai.data['AI as black'][white_move_fen] = black_move_fen
                else:
                    black_move_fen = board.moves_list[i]
                    white_move_fen = board.moves_list[i + 1]
                    ai.data['AI as white'][black_move_fen] = white_move_fen


# Initializing Board and Chess Pieces with default positions
board = Board()
ui = UI()
ai = AI()
w_king = Piece('graphics/Chess-pieces/white-king.png', (4, 7), 'K')
w_queen = Piece('graphics/Chess-pieces/white-queen.png', (3, 7), 'Q')
w_rook1 = Piece('graphics/Chess-pieces/white-rook.png', (0, 7), 'R')
w_bishop1 = Piece('graphics/Chess-pieces/white-bishop.png', (2, 7), 'B')
w_knight1 = Piece('graphics/Chess-pieces/white-knight.png', (1, 7), 'N')
w_rook2 = Piece('graphics/Chess-pieces/white-rook.png', (7, 7), 'R')
w_bishop2 = Piece('graphics/Chess-pieces/white-bishop.png', (5, 7), 'B')
w_knight2 = Piece('graphics/Chess-pieces/white-knight.png', (6, 7), 'N')
w_pawn1 = Piece('graphics/Chess-pieces/white-pawn.png', (0, 6), 'P')
w_pawn2 = Piece('graphics/Chess-pieces/white-pawn.png', (1, 6), 'P')
w_pawn3 = Piece('graphics/Chess-pieces/white-pawn.png', (2, 6), 'P')
w_pawn4 = Piece('graphics/Chess-pieces/white-pawn.png', (3, 6), 'P')
w_pawn5 = Piece('graphics/Chess-pieces/white-pawn.png', (4, 6), 'P')
w_pawn6 = Piece('graphics/Chess-pieces/white-pawn.png', (5, 6), 'P')
w_pawn7 = Piece('graphics/Chess-pieces/white-pawn.png', (6, 6), 'P')
w_pawn8 = Piece('graphics/Chess-pieces/white-pawn.png', (7, 6), 'P')

b_king = Piece('graphics/Chess-pieces/black-king.png', (4, 0), 'k')
b_queen = Piece('graphics/Chess-pieces/black-queen.png', (3, 0), 'q')
b_rook1 = Piece('graphics/Chess-pieces/black-rook.png', (0, 0), 'r')
b_bishop1 = Piece('graphics/Chess-pieces/black-bishop.png', (2, 0), 'b')
b_knight1 = Piece('graphics/Chess-pieces/black-knight.png', (1, 0), 'n')
b_rook2 = Piece('graphics/Chess-pieces/black-rook.png', (7, 0), 'r')
b_bishop2 = Piece('graphics/Chess-pieces/black-bishop.png', (5, 0), 'b')
b_knight2 = Piece('graphics/Chess-pieces/black-knight.png', (6, 0), 'n')
b_pawn1 = Piece('graphics/Chess-pieces/black-pawn.png', (0, 1), 'p')
b_pawn2 = Piece('graphics/Chess-pieces/black-pawn.png', (1, 1), 'p')
b_pawn3 = Piece('graphics/Chess-pieces/black-pawn.png', (2, 1), 'p')
b_pawn4 = Piece('graphics/Chess-pieces/black-pawn.png', (3, 1), 'p')
b_pawn5 = Piece('graphics/Chess-pieces/black-pawn.png', (4, 1), 'p')
b_pawn6 = Piece('graphics/Chess-pieces/black-pawn.png', (5, 1), 'p')
b_pawn7 = Piece('graphics/Chess-pieces/black-pawn.png', (6, 1), 'p')
b_pawn8 = Piece('graphics/Chess-pieces/black-pawn.png', (7, 1), 'p')


def import_fen(fen_string):
    rank = 0
    file = 0

    repeatable_pieces = {
        'r': [b_rook1, b_rook2],
        'n': [b_knight1, b_knight2],
        'b': [b_bishop1, b_bishop2],
        'p': [b_pawn1, b_pawn2, b_pawn3, b_pawn4, b_pawn5, b_pawn6, b_pawn7, b_pawn8],
        'R': [w_rook1, w_rook2],
        'N': [w_knight1, w_knight2],
        'B': [w_bishop1, w_bishop2],
        'P': [w_pawn1, w_pawn2, w_pawn3, w_pawn4, w_pawn5, w_pawn6, w_pawn7, w_pawn8]
    }

    single_pieces = {
        'q': b_queen,
        'k': b_king,
        'Q': w_queen,
        'K': w_king
    }

    for piece in board.pieces_list:
        piece.update_position(None)

    for c in fen_string.split()[0]:
        if c.isnumeric():
            file += int(c)
        elif c == '/':
            file = 0
            rank += 1
        else:
            if c in repeatable_pieces:
                repeatable_pieces[c][0].update_position((file, rank))
                repeatable_pieces[c].pop(0)
            elif c in single_pieces:
                single_pieces[c].update_position((file, rank))
            file += 1


def generate_fen():
    fen = ''

    for rank in range(8):
        empty_squares = 0
        for file in range(8):
            found = False
            for piece in board.pieces_list:
                if piece.position == (file, rank):
                    if empty_squares:
                        fen += str(empty_squares)
                    fen += piece.id
                    empty_squares = 0
                    found = True
                    break
            if not found:
                empty_squares += 1

        if empty_squares:
            fen += str(empty_squares) + '/'
        else:
            fen += '/'

    fen += ' b' if board.move_number % 2 else ' w'

    return fen


import_fen('rnbqkbnr/pppppppp/////PPPPPPPP/RNBQKBNR w')
board.moves_list.append(generate_fen())

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if board.can_move:
                    for piece in board.pieces_list:
                        if piece.rect.collidepoint(event.pos): 
                            Piece.picked = piece
                            board.pieces_list.remove(piece)
                            board.pieces_list.append(piece)
                            break

                if ui.train_text_rect.collidepoint(event.pos):
                    ui.train()

                if ui.learn_text_rect.collidepoint(event.pos) and ui.can_press_learn:
                    print('learning')
                    ui.learn()
            
                if ui.flip_button_rect.collidepoint(event.pos):
                    ui.flip()
            
        if event.type == MOUSEMOTION:
            if Piece.picked:
                Piece.picked.rect.center = event.pos

        if event.type == MOUSEBUTTONUP:
            if Piece.picked and event.button == 1:
                index = board.square_centers.index(board.closest_point(Piece.picked.rect.center, board.square_centers))
                Piece.picked.update_position((index // 8, index % 8))
                for piece in board.pieces_list:
                    if piece != Piece.picked and piece.rect.center == Piece.picked.rect.center:
                        piece.update_position(None)
                        break

                Piece.picked = None
                board.move_number += 1
                board.moves_list.append(generate_fen())
                board.colour_to_move = 'black' if board.colour_to_move == 'white' else 'white'
                ui.refresh()
                ai.move()
                
                
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                if board.move_number > 0:
                    board.move_number -= 1  
                    import_fen(board.moves_list[board.move_number])

                if board.move_number != len(board.moves_list) - 1:
                    board.can_move = False

            if event.key == K_RIGHT:
                if len(board.moves_list) > board.move_number + 1:
                    board.move_number += 1
                    import_fen(board.moves_list[board.move_number])

                if board.move_number == len(board.moves_list) - 1 :
                    board.can_move = True
            
            if event.key == K_z:
                if board.move_number == len(board.moves_list) - 1 and board.move_number:
                    board.moves_list.pop()
                    board.move_number -= 1
                    board.colour_to_move = 'black' if board.colour_to_move == 'white' else 'white'
                    ui.refresh()
                    import_fen(board.moves_list[board.move_number])

    screen.fill('#272521')

    board.draw_board()
    ui.draw()

    clock.tick(60)
    pygame.display.update()


pygame.quit()


