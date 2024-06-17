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
picked_square_color = 'yellow'
prev_square_color = 'light blue'
next_square_color = 'blue'


class Board:
    def __init__(self):
        self.square_list = [[None for _ in range(8)] for _ in range(8)]
        self.pieces_pos_list = [[None for _ in range(8)] for _ in range(8)]
        self.square_centers = []
        self.pieces_list = []
        self.moves_list = []
        self.move_number = 0
        self.can_move = True
        self.user_colour = 'w'
        self.colour_to_move = 'w'
        self.move_squares = []
        self.move_squares_list = []
        self.initialise_board()

    def initialise_board(self):
        for i in range(8):
            for j in range(8):
                square_surf = pygame.Surface((square_size, square_size))
                square_rect = square_surf.get_rect(topleft = (i * square_size, j * square_size))
                self.square_centers.append(square_rect.center)
                if ((i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1)):
                    square_surf.fill(light_square_color)
                    self.square_list[i][j] = (square_surf, square_rect, light_square_color)
                else:
                    square_surf.fill(dark_square_color)
                    self.square_list[i][j] = (square_surf, square_rect, dark_square_color)

    def get_piece_on_square(self, square):
        for piece in board.pieces_list:
            if piece.get_square() == square:
                return piece

    def get_square_index(self, square):
        for i, sublist in enumerate(self.square_list):
            if square in sublist:
                return (i, sublist.index(square))

    def closest_point(self, point, points):
        min_distance = float('inf')
        closest = None
        
        for p in points:
            distance = math.sqrt((point[0] - p[0])**2 + (point[1] - p[1])**2)
            if distance < min_distance:
                min_distance = distance
                closest = p
        
        return closest

    def update_move_squares(self, index=None):
        if self.move_squares:
            sq1, sq2 = [board.square_list[p[0]][p[1]] for p in self.move_squares]
            sq1[0].fill(sq1[2])
            sq2[0].fill(sq2[2])

        index = index if index else board.move_number
        index -= 1

        if index < 0:
            return

        self.move_squares = self.move_squares_list[index]
        sq1, sq2 = [board.square_list[p[0]][p[1]] for p in self.move_squares_list[index]]
        sq1[0].fill(prev_square_color)
        sq2[0].fill(next_square_color)

    def get_positions_changed(self, prev_move_number, next_move_number):
        changed_squares = [
            {
                'prev': None,
                'next': None
            },
            {
                'prev': None,
                'next': None
            }
        ]
        sq_list = [item for sublist in board.square_list for item in sublist]

        import_fen(board.moves_list[prev_move_number])
        prev_board_state = [board.get_piece_on_square(square) for square in sq_list]

        import_fen(board.moves_list[next_move_number])
        next_board_state = [board.get_piece_on_square(square) for square in sq_list]

        for i, square in enumerate(sq_list):
            prev_piece = prev_board_state[i]
            next_piece = next_board_state[i]

            if prev_piece is not None and next_piece is None:
                if changed_squares[0]['prev']:
                    changed_squares[1]['prev'] = square
                else:
                    changed_squares[0]['prev'] = square
            elif prev_piece is None and next_piece is not None:
                if changed_squares[0]['next']:
                    changed_squares[1]['next'] = square
                else:
                    changed_squares[0]['next'] = square
            elif prev_piece == None and next_piece == None:
                pass
            elif prev_piece.id != next_piece.id:
                if changed_squares[0]['next']:
                    changed_squares[1]['next'] = square
                else:
                    changed_squares[0]['next'] = square
                
        if not changed_squares[1]['next']:
            changed_squares = [changed_squares[0]['prev'], changed_squares[0]['next']]
        else:
            if self.get_square_index(changed_squares[0]['prev']) == (0, 0):
                changed_squares = [changed_squares[1]['prev'], changed_squares[0]['prev']]
            else: 
                changed_squares = [changed_squares[0]['prev'], changed_squares[1]['prev']]
                
        return changed_squares

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
        self.colour = 'w' if self.id.isupper() else 'b'
        self.position = position
        board.pieces_pos_list[position[0]][position[1]] = self
        board.pieces_list.append(self)
        self.update_position(self.position)

    def update_position(self, position):
        self.position = position
        self.rect.topleft = (self.position[0] * square_size, self.position[1] * square_size)
        self.rect.center = board.closest_point(self.rect.center, board.square_centers)

    def get_position(self):
        return self.position

    def get_square(self):
        return board.square_list[self.position[0]][self.position[1]]

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
        if board.user_colour == 'w' and board.colour_to_move == 'w':
            self.can_press_learn = True
        elif board.user_colour == 'b' and board.colour_to_move == 'b':
            self.can_press_learn = True
        else:
            self.can_press_learn = False

    def train(self):
        with open('data.json', 'r') as file:
            ai.data = json.load(file)

        ai.is_training = True
        ai.move()

    def flip(self):
        board.user_colour = 'w' if board.user_colour == 'b' else 'b'
        fen = ''
        old_fen = generate_fen()
        fen = old_fen.split()[0][-2::-1] + ' ' + ' '.join(old_fen.split()[1:])
        
        import_fen(fen)
        ui.refresh()

    def learn(self):
        if not ai.is_learning:
            ai.is_learning = True
            if board.user_colour == 'w':
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

        ai_colour = 'b' if board.user_colour == 'w' else 'w'
        fen = ai.data[ai_colour][generate_fen()]
        board.move_number += 1
        import_fen(fen)
        board.moves_list.append(fen)
        board.colour_to_move = 'b' if board.colour_to_move == 'w' else 'w'

        squares = board.get_positions_changed(board.move_number - 1, board.move_number)
        board.move_squares_list.append([board.get_square_index(square) for square in squares])
        board.update_move_squares()

    def learn(self):
        for i in range(self.start_move, self.end_move, 2):
            if i + 1 < len(board.moves_list):
                if board.user_colour == 'w': 
                    white_move_fen = board.moves_list[i]
                    black_move_fen = board.moves_list[i + 1]
                    ai.data['b'][white_move_fen] = black_move_fen
                else:
                    black_move_fen = board.moves_list[i]
                    white_move_fen = board.moves_list[i + 1]
                    ai.data['w'][black_move_fen] = white_move_fen


class GameManager:
    def __init__(self, board, ui, ai):
        self.board = board
        self.ui = ui
        self.ai = ai
        self.can_en_passant = False
        self.castle_info = 'KQkq'

    def update(self):
        pass

    def update_castling(self, piece, pos):
        if piece.id == 'K':
            self.castle_info = ''.join([char for char in self.castle_info if char.islower()])
            self.castle_info = '-' if not self.castle_info else self.castle_info
            return
        elif piece.id == 'k':
            self.castle_info = ''.join([char for char in self.castle_info if char.isupper()])
            self.castle_info = '-' if not self.castle_info else self.castle_info
            return

        if not piece.id.lower() == 'r':
            return

        if pos == (0, 0):
            if board.user_colour == 'w':
                self.castle_info = self.castle_info.replace('q', '')
            else:
                self.castle_info = self.castle_info.replace('K', '')
        elif pos == (7, 0):
            if board.user_colour == 'w':
                self.castle_info = self.castle_info.replace('k', '')
            else:
                self.castle_info = self.castle_info.replace('Q', '')
        elif pos == (0, 7):
            if board.user_colour == 'w':
                self.castle_info = self.castle_info.replace('Q', '')
            else:
                self.castle_info = self.castle_info.replace('k', '')
        elif pos == (7, 7):
            if board.user_colour == 'w':
                self.castle_info = self.castle_info.replace('K', '')
            else:
                self.castle_info = self.castle_info.replace('q', '')

        self.castle_info = '-' if not self.castle_info else self.castle_info

    def castle(self, king, rook, old_pos):
        if not (king.id.lower() == 'k' and rook.id.lower() == 'r'):
            return False            
        
        king_pos = old_pos
        rook_pos = rook.get_position()
        castled = False

        if king_pos[0] < rook_pos[0]:
            for i in range(king_pos[0] + 1, rook_pos[0]):
                sq = self.board.square_list[i][king_pos[1]]
                if self.board.get_piece_on_square(sq):
                    return False

        else:
            for i in range(rook_pos[0] + 1, king_pos[0]):
                sq = self.board.square_list[i][king_pos[1]]
                if self.board.get_piece_on_square(sq):
                    return False
        
        if self.board.user_colour == 'w':
            if (rook_pos == (0, 0) and self.castle_info.find('q') != -1) or (rook_pos == (0, 7) and self.castle_info.find('Q') != -1):
                king_pos = (2, king_pos[1])
                rook_pos = (3, rook_pos[1])
                castled = True
            elif (rook_pos == (7, 0) and self.castle_info.find('k') != -1) or (rook_pos == (7, 7) and self.castle_info.find('K') != -1):
                king_pos = (6, king_pos[1])
                rook_pos = (5, rook_pos[1])
                castled = True
        else:
            if (rook_pos == (0, 0) and self.castle_info.find('K') != -1) or (rook_pos == (0, 7) and self.castle_info.find('k') != -1):
                king_pos = (1, king_pos[1])
                rook_pos = (2, rook_pos[1])
                castled = True
            elif (rook_pos == (7, 0) and self.castle_info.find('Q') != -1) or (rook_pos == (7, 7) and self.castle_info.find('q') != -1):
                king_pos = (5, king_pos[1])
                rook_pos = (4, rook_pos[1])
                castled = True
        
        if not castled:
            return False

        if king.colour == 'w': 
            self.castle_info = ''.join([char for char in self.castle_info if char.islower()])
        else:
            self.castle_info = ''.join([char for char in self.castle_info if char.isupper()])

        self.castle_info = '-' if not self.castle_info else self.castle_info

        king.update_position(king_pos) 
        rook.update_position(rook_pos) 

        return True


# Initializing Board and Chess Pieces with default positions
board = Board()
ui = UI()
ai = AI()
game_manager = GameManager(board, ui, ai)
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

    board.pieces_list = []

    for c in fen_string.split()[0]:
        if c.isnumeric():
            file += int(c)
        elif c == '/':
            file = 0
            rank += 1
        else:
            if c in repeatable_pieces:
                board.pieces_list.append(repeatable_pieces[c][0])
                repeatable_pieces[c][0].update_position((file, rank))
                repeatable_pieces[c].pop(0)
            elif c in single_pieces:
                board.pieces_list.append(single_pieces[c])
                single_pieces[c].update_position((file, rank))
            file += 1
        
    board.colour_to_move = fen_string.split()[1]
    game_manager.castle_info = fen_string.split()[2]


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
    fen += ' ' + game_manager.castle_info

    return fen


import_fen('rnbqkbnr/pppppppp/////PPPPPPPP/RNBQKBNR w KQkq')
board.moves_list.append(generate_fen())

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if ui.train_text_rect.collidepoint(event.pos):
                    ui.train()

                elif ui.learn_text_rect.collidepoint(event.pos) and ui.can_press_learn:
                    ui.learn()
            
                elif ui.flip_button_rect.collidepoint(event.pos):
                    ui.flip()

                elif board.can_move:
                    for piece in board.pieces_list:
                        if piece.rect.collidepoint(event.pos): 
                            if piece.colour != board.colour_to_move:
                                continue
                            Piece.picked = piece
                            piece.rect.center = event.pos
                            piece.get_square()[0].fill(picked_square_color)
                            board.pieces_list.remove(piece)
                            board.pieces_list.append(piece)
                            break

            
        if event.type == MOUSEMOTION:
            if Piece.picked:
                Piece.picked.rect.center = event.pos

        if event.type == MOUSEBUTTONUP:
            if Piece.picked and event.button == 1:
                valid_move = True
                square = Piece.picked.get_square()
                square[0].fill(square[2])

                index = board.square_centers.index(board.closest_point(Piece.picked.rect.center, board.square_centers))
                old_pos = Piece.picked.get_position()
                new_pos = index // 8, index % 8

                if old_pos == new_pos:
                    Piece.picked.update_position(old_pos)
                    Piece.picked = None
                    continue

                Piece.picked.update_position(new_pos)

                for piece in board.pieces_list:
                    if Piece.picked != piece and piece.get_position() == new_pos:
                        if piece.colour == Piece.picked.colour:
                            if not game_manager.castle(Piece.picked, piece, old_pos):
                                valid_move = False
                        else:
                            board.pieces_list.remove(piece)
                        break

                if not valid_move:
                    Piece.picked.update_position(old_pos)
                    Piece.picked = None
                    continue

                game_manager.update_castling(Piece.picked, old_pos)

                Piece.picked = None
                board.move_squares_list.append([old_pos, new_pos])
                board.move_number += 1
                board.update_move_squares()
                board.moves_list.append(generate_fen())
                board.colour_to_move = 'b' if board.colour_to_move == 'w' else 'w'

                ui.refresh()
                ai.move()
                
                
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                if board.move_number > 0:
                    board.move_number -= 1  
                    import_fen(board.moves_list[board.move_number])

                    board.update_move_squares()

                if board.move_number != len(board.moves_list) - 1:
                    board.can_move = False

            elif event.key == K_RIGHT:
                if len(board.moves_list) > board.move_number + 1:
                    board.move_number += 1
                    import_fen(board.moves_list[board.move_number])

                    board.update_move_squares()

                if board.move_number == len(board.moves_list) - 1 :
                    board.can_move = True
            
            elif event.key == K_z:
                if board.move_number == len(board.moves_list) - 1 and board.move_number:
                    board.move_number -= 1
                    board.colour_to_move = 'b' if board.colour_to_move == 'w' else 'w'
                    ui.refresh()
                    import_fen(board.moves_list[board.move_number])

                    board.move_squares_list.pop()
                    board.moves_list.pop()
                    board.update_move_squares()

    screen.fill('#272521')

    board.draw_board()
    ui.draw()

    clock.tick(60)
    pygame.display.update()


pygame.quit()


