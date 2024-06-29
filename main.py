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
        self.possible_moves_list = []
        self.hover_pos = None    
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
        for piece in self.pieces_list:
            if piece.get_square() == square:
                return piece

    def get_piece_on_pos(self, pos):
        for piece in self.pieces_list:
            if piece.get_position() == pos:
                return piece

    def get_square_index(self, square):
        for i, sublist in enumerate(self.square_list):
            if square in sublist:
                return (i, sublist.index(square))

    def get_square(self, index):
        return self.square_list[index[0]][index[1]]
    
    def closest_point(self, point, points):
        min_distance = float('inf')
        closest = None
        
        for p in points:
            distance = math.sqrt((point[0] - p[0])**2 + (point[1] - p[1])**2)
            if distance < min_distance:
                min_distance = distance
                closest = p
        
        return closest

    def highlight_possible_moves(self):
        for x, y in self.possible_moves_list:
            if (x, y) == self.hover_pos:
                pygame.draw.rect(screen, 'grey', (x * square_size, y * square_size, square_size, square_size), 10)

            center = (x * square_size + square_size // 2, y * square_size + square_size // 2)
            if self.get_piece_on_pos((x, y)):
                pygame.draw.circle(screen, 'grey', center, square_size // 2, 10)
            else:
                pygame.draw.circle(screen, 'grey', center, 20)

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

        import_fen(board.moves_list[next_move_number])
        next_board_state = [board.get_piece_on_square(square) for square in sq_list]

        import_fen(board.moves_list[prev_move_number])
        prev_board_state = [board.get_piece_on_square(square) for square in sq_list]

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
                
        if not changed_squares[1]['prev']:
            changed_squares = [changed_squares[0]['prev'], changed_squares[0]['next']]
        elif changed_squares[1]['next']:
            if self.get_square_index(changed_squares[0]['prev']) == (0, 0):
                changed_squares = [changed_squares[1]['prev'], changed_squares[0]['prev'], 
                                    changed_squares[0]['next'], changed_squares[1]['next']]
            else: 
                changed_squares = [changed_squares[0]['prev'], changed_squares[1]['prev'], 
                                    changed_squares[1]['next'], changed_squares[0]['next']]
        else:
            if self.get_square_index(changed_squares[0]['prev'])[0] < self.get_square_index(changed_squares[0]['next'])[0]:
                changed_squares = [changed_squares[0]['prev'], changed_squares[0]['next'], changed_squares[1]['prev']]
            else:
                changed_squares = [changed_squares[1]['prev'], changed_squares[0]['next'], changed_squares[0]['prev']]
                
        return changed_squares

    def draw_board(self):
        for i in range(8):
            for j in range(8):
                square = self.square_list[i][j]
                screen.blit(square[0], square[1])

        self.highlight_possible_moves()

        for piece in self.pieces_list:
            piece.update_animation()
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
        self.animating = False
        self.time = 0
        self.duration = 30
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

    def ease_in_out(self, t):
        if t < 0.5:
            return 8 * t ** 4
        else:
            return 1 - 8 * (1 - t) ** 4

    def animate_move(self, start_pos, end_pos):
        self.start_pos = (start_pos[0] * square_size, start_pos[1] * square_size)
        self.end_pos = (end_pos[0] * square_size, end_pos[1] * square_size)
        board.pieces_list.remove(self)
        board.pieces_list.append(self)
        self.animating = True
        self.time = 0

    def update_animation(self):
        if self.animating:
            t = self.time / self.duration
            t = self.ease_in_out(t)
            if t >= 1:
                t = 1
                self.animating = False
                self.update_position((self.end_pos[0] // square_size, self.end_pos[1] // square_size))
                fen = board.moves_list[board.move_number]
                board.colour_to_move = fen.split()[1]
                game_manager.castle_info = fen.split()[2]
                game_manager.en_passant_target_square = fen.split()[3]
                ui.refresh()
                game_manager.update_legal_moves()
                return

            self.rect.topleft = (
                self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t,
                self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
            )
            self.time += 1


class Rook(Piece):
    def generate_moves(self, only_attack_moves=False):

        move_offsets = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        possible_moves = []

        for offset in move_offsets:
            x, y = self.get_position()
            while True:
                x += offset[0]
                y += offset[1]

                if 0 <= x < 8 and 0 <= y < 8:
                    target_square = board.square_list[x][y]                
                    piece = board.get_piece_on_square(target_square)
                    if not piece:
                        possible_moves.append((x, y))
                    else:
                        if piece.colour != self.colour:
                            possible_moves.append((x, y))
                        break
                else:
                    break

        return possible_moves


class King(Piece):
    def generate_moves(self, only_attack_moves=False):
        move_offsets = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        possible_moves = []

        for i in [0, 7]:
            pos = (i, self.get_position()[1])
            rook = board.get_piece_on_pos(pos)
            if rook and rook.id.lower() == 'r' and rook.colour == self.colour:
                if game_manager.can_castle(self, rook):
                    possible_moves.append(pos)
                
        for offset in move_offsets:
            x, y = self.get_position()
            x += offset[0]
            y += offset[1]

            if 0 <= x < 8 and 0 <= y < 8:
                target_square = board.square_list[x][y]                
                piece = board.get_piece_on_square(target_square)
                if not piece:
                    possible_moves.append((x, y))
                else:
                    if piece.colour != self.colour:
                        possible_moves.append((x, y))

        return possible_moves


class Queen(Piece):
    def generate_moves(self, only_attack_moves=False):
        move_offsets = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        possible_moves = []

        for offset in move_offsets:
            x, y = self.get_position()
            while True:
                x += offset[0]
                y += offset[1]

                if 0 <= x < 8 and 0 <= y < 8:
                    target_square = board.square_list[x][y]                
                    piece = board.get_piece_on_square(target_square)
                    if not piece:
                        possible_moves.append((x, y))
                    else:
                        if piece.colour != self.colour:
                            possible_moves.append((x, y))
                        break
                else:
                    break

        return possible_moves
    

class Knight(Piece):
    def generate_moves(self, only_attack_moves=False):
        move_offsets = [(-2, -1), (-2, 1), (2, -1), (2, 1),
                        (-1, -2), (-1, 2), (1, -2), (1, 2)]
        possible_moves = []

        for offset in move_offsets:
            x, y = self.get_position()
            x += offset[0]
            y += offset[1]

            if 0 <= x < 8 and 0 <= y < 8:
                target_square = board.square_list[x][y]                
                piece = board.get_piece_on_square(target_square)
                if not piece:
                    possible_moves.append((x, y))
                else:
                    if piece.colour != self.colour:
                        possible_moves.append((x, y))

        return possible_moves


class Bishop(Piece):
    def generate_moves(self, only_attack_moves=False):
        move_offsets = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        possible_moves = []

        for offset in move_offsets:
            x, y = self.get_position()
            while True:
                x += offset[0]
                y += offset[1]

                if 0 <= x < 8 and 0 <= y < 8:
                    target_square = board.square_list[x][y]                
                    piece = board.get_piece_on_square(target_square)
                    if not piece:
                        possible_moves.append((x, y))
                    else:
                        if piece.colour != self.colour:
                            possible_moves.append((x, y))
                        break
                else:
                    break

        return possible_moves


class Pawn(Piece):
    def generate_moves(self, only_attack_moves=False):
        if self.colour == board.user_colour:
            move_offsets = [(0, -1), (0, -2), (1, -1), (-1, -1)]
            initial_y = 6
        else:
            move_offsets = [(0, 1), (0, 2), (1, 1), (-1, 1)]
            initial_y = 1

        possible_moves = []

        if only_attack_moves:
            for offset in move_offsets:
                x, y = self.get_position()
                x += offset[0]
                y += offset[1]

                if not (0 <= x < 8 and 0 <= y < 8):
                    continue

                # Forward_moves
                if offset[0] == 0:
                    continue

                # En passant 
                if abs(offset[0]) == 1:
                    if game_manager.en_passant_target_square == game_manager.index_to_chess_notation((x, y)):
                        possible_moves.append((x, y))
                        continue
                
                possible_moves.append((x, y))

            return possible_moves

        for offset in move_offsets:
            x, y = self.get_position()
            x += offset[0]
            y += offset[1]

            if not (0 <= x < 8 and 0 <= y < 8):
                continue

            # Initial two square move
            if abs(offset[1]) == 2:
                x, y = self.get_position()
                if y != initial_y:
                    continue

                sq1 = board.square_list[x][y + move_offsets[0][1]]
                sq2 = board.square_list[x][y + offset[1]]
                if not (board.get_piece_on_square(sq1) or board.get_piece_on_square(sq2)):
                    possible_moves.append((x, y + offset[1]))
                continue

            # En passant 
            if abs(offset[0]) == 1:
                if game_manager.en_passant_target_square == game_manager.index_to_chess_notation((x, y)):
                    possible_moves.append((x, y))
                    continue

            target_square = board.square_list[x][y]                
            piece = board.get_piece_on_square(target_square)
            if not piece and offset[0] == 0:
                possible_moves.append((x, y))
            elif piece and offset[0] != 0:
                if piece.colour != self.colour:
                    possible_moves.append((x, y))

        return possible_moves


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

        ai.is_training = True if not ai.is_training else False
        print('training started' if ai.is_training else 'training stopped')
        ai.move()

    def flip(self):
        board.user_colour = 'w' if board.user_colour == 'b' else 'b'
        fen = ''
        old_fen = generate_fen()
        fen = old_fen.split()[0][-2::-1] + ' ' + ' '.join(old_fen.split()[1:])
        
        import_fen(fen)
        game_manager.update_legal_moves()
        ui.refresh()

    def learn(self):
        if not ai.is_learning:
            print('learning')
            ai.is_learning = True
            if board.user_colour == 'w':
                ai.start_move = board.move_number + 1

            with open('data.json', 'r') as file:
                ai.data = json.load(file)

        else:
            print('finished')
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
        ai_colour = 'b' if board.user_colour == 'w' else 'w'
        fen = ai.data[ai_colour][generate_fen()]
        board.moves_list.append(fen)
        board.move_number += 1

        squares = board.get_positions_changed(board.move_number - 1, board.move_number)
        if len(squares) == 4:
            game_manager.move_piece(squares[0], squares[2])
            game_manager.move_piece(squares[1], squares[3])
        elif len(squares) == 3:
            game_manager.move_piece(squares[0], squares[1])
            board.pieces_list.remove(board.get_piece_on_square(squares[2]))
        else:
            game_manager.move_piece(squares[0], squares[1])
            piece = board.get_piece_on_square(squares[1])
            if piece: board.pieces_list.remove(piece)

        board.move_squares_list.append([board.get_square_index(squares[0]), board.get_square_index(squares[1])])
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
    def __init__(self):
        self.en_passant_target_square = '-'
        self.castle_info = 'KQkq'
        self.castling_in_progress = False
        self.legal_moves_dict = {}

    def update(self):
        pass

    def move_piece(self, start_square, end_square):
        start_index = board.get_square_index(start_square)
        end_index = board.get_square_index(end_square)

        piece = board.get_piece_on_square(start_square)
        piece.animate_move(start_index, end_index)

    def index_to_chess_notation(self, index):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        file = files[index[0]]
        rank = ranks[7 - index[1]]
        
        return f"{file}{rank}"
    
    def chess_notation_to_index(self, notation):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        file = notation[0]
        rank = notation[1]
        
        file_index = files.index(file)
        rank_index = 7 - ranks.index(rank)
        
        return (file_index, rank_index)

    def is_king_in_check(self, king):
        king_position = king.get_position()
        for piece in board.pieces_list:
            if piece.colour != board.colour_to_move:
                attack_moves = piece.generate_moves(only_attack_moves=True)
                if king_position in attack_moves:
                    return True
        return False

    def update_legal_moves(self):
        for piece in board.pieces_list:
            if piece.id.lower() == 'k' and piece.colour == board.colour_to_move:
                king = piece

        for piece in board.pieces_list.copy():
            if piece.colour == board.colour_to_move:
                legal_moves = []
                possible_moves = piece.generate_moves()
                old_pos = piece.get_position()

                for move in possible_moves:
                    enemy_piece = board.get_piece_on_pos(move)
                    if enemy_piece and enemy_piece.colour != board.colour_to_move:
                        board.pieces_list.remove(enemy_piece)
                    piece.update_position(move) 

                    if not self.is_king_in_check(king):
                       legal_moves.append(move) 

                    piece.update_position(old_pos)
                    if enemy_piece:
                        board.pieces_list.append(enemy_piece)

                self.legal_moves_dict[piece] = legal_moves

    def en_passant(self, pawn, old_pos):
        new_pos = pawn.get_position()

        if pawn.id.lower() == 'p' and self.en_passant_target_square != '-':
            target_index = self.chess_notation_to_index(self.en_passant_target_square)
            if new_pos == target_index:
                captured_pawn = board.get_piece_on_square(board.square_list[new_pos[0]][old_pos[1]])
                board.pieces_list.remove(captured_pawn)
                self.en_passant_target_square = '-'
                return

        if pawn.id.lower() == 'p':
            if abs(new_pos[1] - old_pos[1]) == 2:
                mid_index = (old_pos[0], (new_pos[1] + old_pos[1]) // 2)
                self.en_passant_target_square = self.index_to_chess_notation(mid_index)
            else:
                self.en_passant_target_square = '-'
        else:
            self.en_passant_target_square = '-'

    def update_castling_rights(self, piece, pos):
        if piece.id.lower() == 'k': 
            if piece.id == 'K':
                self.castle_info = ''.join([char for char in self.castle_info if char.islower()])
            else:
                self.castle_info = ''.join([char for char in self.castle_info if char.isupper()])
            self.castle_info = '-' if not self.castle_info else self.castle_info
            return

        if not piece.id.lower() == 'r':
            return

        rook_pos_map_w = {(0, 0): 'q', (7, 0): 'k', (0, 7): 'Q', (7, 7): 'K'}
        rook_pos_map_b = {(0, 0): 'k', (7, 0): 'Q', (0, 7): 'k', (7, 7): 'q'}

        if board.user_colour == 'w':
            char_to_remove = rook_pos_map_w.get(pos)
        else:
            char_to_remove = rook_pos_map_b.get(pos)

        if char_to_remove:
            self.castle_info = self.castle_info.replace(char_to_remove, '')
            self.castle_info = '-' if not self.castle_info else self.castle_info

    def can_castle(self, king, rook):
        if self.castling_in_progress:
            return False

        if not (king.id.lower() == 'k' and rook.id.lower() == 'r'):
            return False

        king_pos = king.get_position()
        rook_pos = rook.get_position()
        direction = 1 if king_pos[0] < rook_pos[0] else -1
        path = [(king_pos[0] + i * direction, king_pos[1]) for i in range(1, abs(king_pos[0] - rook_pos[0]))]

        # Check if path is clear
        for sq in path:
            if board.get_piece_on_pos(sq):
                return False

        # Check if path is attacked
        self.castling_in_progress = True
        for piece in board.pieces_list:
            if piece.colour != king.colour:
                attack_positions = piece.generate_moves(only_attack_moves=True)
                for pos in attack_positions:
                    if pos in path:
                        self.castling_in_progress = False
                        return False

        self.castling_in_progress = False

        if board.user_colour == 'w':
            if (rook_pos == (0, 0) and 'q' in self.castle_info) or (rook_pos == (0, 7) and 'Q' in self.castle_info):
                return True
            if (rook_pos == (7, 0) and 'k' in self.castle_info) or (rook_pos == (7, 7) and 'K' in self.castle_info):
                return True
        else:
            if (rook_pos == (0, 0) and 'K' in self.castle_info) or (rook_pos == (0, 7) and 'k' in self.castle_info):
                return True
            if (rook_pos == (7, 0) and 'Q' in self.castle_info) or (rook_pos == (7, 7) and 'q' in self.castle_info):
                return True

        return False

    def castle(self, king, rook):
        if not self.can_castle(king, rook):
            return False
        
        king_pos = king.get_position()
        rook_pos = rook.get_position()
        direction = 1 if king_pos[0] < rook_pos[0] else -1

        if direction == 1:  # King-side castling
            new_king_pos = (king_pos[0] + 2, king_pos[1])
            new_rook_pos = (king_pos[0] + 1, rook_pos[1])
        else:  # Queen-side castling
            new_king_pos = (king_pos[0] - 2, king_pos[1])
            new_rook_pos = (king_pos[0] - 1, rook_pos[1])        

        if king.colour == 'w': 
            self.castle_info = ''.join([char for char in self.castle_info if char.islower()])
        else:
            self.castle_info = ''.join([char for char in self.castle_info if char.isupper()])

        self.castle_info = '-' if not self.castle_info else self.castle_info
        rook.update_position(new_rook_pos) 
        return new_king_pos


# Initializing Board and Chess Pieces with default positions
board = Board()
ui = UI()
ai = AI()
game_manager = GameManager()
w_king = King('graphics/Chess-pieces/white-king.png', (4, 7), 'K')
w_queen = Queen('graphics/Chess-pieces/white-queen.png', (3, 7), 'Q')
w_rook1 = Rook('graphics/Chess-pieces/white-rook.png', (0, 7), 'R')
w_bishop1 = Bishop('graphics/Chess-pieces/white-bishop.png', (2, 7), 'B')
w_knight1 = Knight('graphics/Chess-pieces/white-knight.png', (1, 7), 'N')
w_rook2 = Rook('graphics/Chess-pieces/white-rook.png', (7, 7), 'R')
w_bishop2 = Bishop('graphics/Chess-pieces/white-bishop.png', (5, 7), 'B')
w_knight2 = Knight('graphics/Chess-pieces/white-knight.png', (6, 7), 'N')
w_pawn1 = Pawn('graphics/Chess-pieces/white-pawn.png', (0, 6), 'P')
w_pawn2 = Pawn('graphics/Chess-pieces/white-pawn.png', (1, 6), 'P')
w_pawn3 = Pawn('graphics/Chess-pieces/white-pawn.png', (2, 6), 'P')
w_pawn4 = Pawn('graphics/Chess-pieces/white-pawn.png', (3, 6), 'P')
w_pawn5 = Pawn('graphics/Chess-pieces/white-pawn.png', (4, 6), 'P')
w_pawn6 = Pawn('graphics/Chess-pieces/white-pawn.png', (5, 6), 'P')
w_pawn7 = Pawn('graphics/Chess-pieces/white-pawn.png', (6, 6), 'P')
w_pawn8 = Pawn('graphics/Chess-pieces/white-pawn.png', (7, 6), 'P')

b_king = King('graphics/Chess-pieces/black-king.png', (4, 0), 'k')
b_queen = Queen('graphics/Chess-pieces/black-queen.png', (3, 0), 'q')
b_rook1 = Rook('graphics/Chess-pieces/black-rook.png', (0, 0), 'r')
b_bishop1 = Bishop('graphics/Chess-pieces/black-bishop.png', (2, 0), 'b')
b_knight1 = Knight('graphics/Chess-pieces/black-knight.png', (1, 0), 'n')
b_rook2 = Rook('graphics/Chess-pieces/black-rook.png', (7, 0), 'r')
b_bishop2 = Bishop('graphics/Chess-pieces/black-bishop.png', (5, 0), 'b')
b_knight2 = Knight('graphics/Chess-pieces/black-knight.png', (6, 0), 'n')
b_pawn1 = Pawn('graphics/Chess-pieces/black-pawn.png', (0, 1), 'p')
b_pawn2 = Pawn('graphics/Chess-pieces/black-pawn.png', (1, 1), 'p')
b_pawn3 = Pawn('graphics/Chess-pieces/black-pawn.png', (2, 1), 'p')
b_pawn4 = Pawn('graphics/Chess-pieces/black-pawn.png', (3, 1), 'p')
b_pawn5 = Pawn('graphics/Chess-pieces/black-pawn.png', (4, 1), 'p')
b_pawn6 = Pawn('graphics/Chess-pieces/black-pawn.png', (5, 1), 'p')
b_pawn7 = Pawn('graphics/Chess-pieces/black-pawn.png', (6, 1), 'p')
b_pawn8 = Pawn('graphics/Chess-pieces/black-pawn.png', (7, 1), 'p')


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
    game_manager.en_passant_target_square = fen_string.split()[3]


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
    fen += ' ' + game_manager.en_passant_target_square

    return fen


import_fen('rnbqkbnr/pppppppp/////PPPPPPPP/RNBQKBNR w KQkq -')
board.moves_list.append(generate_fen())
game_manager.update_legal_moves()

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
                            board.possible_moves_list = game_manager.legal_moves_dict[piece]
                            break
            
        if event.type == MOUSEMOTION:
            if Piece.picked:
                Piece.picked.rect.center = event.pos
                found = False

                for pos in board.possible_moves_list:
                    sq = board.get_square(pos)
                    if sq[1].collidepoint(event.pos):
                        board.hover_pos = pos
                        found = True
                
                if not found:
                    board.hover_pos = None

        if event.type == MOUSEBUTTONUP:
            if Piece.picked and event.button == 1:
                square = Piece.picked.get_square()
                square[0].fill(square[2])

                index = board.square_centers.index(board.closest_point(Piece.picked.rect.center, board.square_centers))
                old_pos = Piece.picked.get_position()
                new_pos = index // 8, index % 8

                if new_pos not in board.possible_moves_list:
                    Piece.picked.update_position(old_pos)
                    Piece.picked = None
                    board.possible_moves_list = []
                    continue
                
                piece = board.get_piece_on_pos(new_pos)
                if piece and piece.colour != board.colour_to_move: 
                    board.pieces_list.remove(piece) 
                elif piece and piece.colour == board.colour_to_move:
                    new_pos = game_manager.castle(Piece.picked, piece)

                Piece.picked.update_position(new_pos)

                game_manager.en_passant(Piece.picked, old_pos)
                game_manager.update_castling_rights(Piece.picked, old_pos)

                Piece.picked = None
                board.possible_moves_list = []
                board.hover_pos = None
                board.move_squares_list.append([old_pos, new_pos])
                board.move_number += 1
                board.update_move_squares()
                board.moves_list.append(generate_fen())
                board.colour_to_move = 'b' if board.colour_to_move == 'w' else 'w'

                if ai.is_training:
                    ai.move()
                else:
                    ui.refresh()
                    game_manager.update_legal_moves()
                
                
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
                    import_fen(board.moves_list[board.move_number])

                    board.move_squares_list.pop()
                    board.moves_list.pop()
                    board.update_move_squares()
                    ui.refresh()
                    game_manager.update_legal_moves()
            
            elif event.key == K_f:
                print(generate_fen())

    screen.fill('#272521')

    board.draw_board()
    ui.draw()

    clock.tick(60)
    pygame.display.update()


pygame.quit()


