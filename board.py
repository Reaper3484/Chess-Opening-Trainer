import pygame
from pygame.locals import *
from constants import *
from state_manager import AppState
import math
from chess_logic import GameManager


class Board:
    def __init__(self, screen, state_manager, pos=(0, 0), padding=BUTTON_PADDING):
        self.screen = screen
        self.control_down = False
        self.game_manager = GameManager(self, state_manager)
        self.state_manager = state_manager
        self.board_pos = pos
        self.rect = pygame.Rect(self.board_pos[0] + padding, self.board_pos[1] + padding, SQUARE_SIZE * 8, SQUARE_SIZE * 8)
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
        self.notations_list = []
        self.initialize_board()
        self.initialize_pieces()
        self.reset_board('w')
    
    def initialize_board(self):
        for i in range(8):
            for j in range(8):
                square_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                square_pos = (i * SQUARE_SIZE + self.board_pos[0], j * SQUARE_SIZE + self.board_pos[1])
                square_rect = square_surf.get_rect(topleft = square_pos)
                self.square_centers.append(square_rect.center)
                if ((i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1)):
                    square_surf.fill(LIGHT_SQUARE_COLOR)
                    self.square_list[i][j] = (square_surf, square_rect, LIGHT_SQUARE_COLOR)
                else:
                    square_surf.fill(DARK_SQUARE_COLOR)
                    self.square_list[i][j] = (square_surf, square_rect, DARK_SQUARE_COLOR)

    def initialize_pieces(self):
        self.w_king = King(CHESS_PIECES_PATH + 'white-king.png', (4, 7), 'K', self.game_manager, self, self.screen)
        self.w_queen = Queen(CHESS_PIECES_PATH + 'white-queen.png', (3, 7), 'Q', self.game_manager, self, self.screen)
        self.w_rook1 = Rook(CHESS_PIECES_PATH + 'white-rook.png', (0, 7), 'R', self.game_manager, self, self.screen)
        self.w_bishop1 = Bishop(CHESS_PIECES_PATH + 'white-bishop.png', (2, 7), 'B', self.game_manager, self, self.screen)
        self.w_knight1 = Knight(CHESS_PIECES_PATH + 'white-knight.png', (1, 7), 'N', self.game_manager, self, self.screen)
        self.w_rook2 = Rook(CHESS_PIECES_PATH + 'white-rook.png', (7, 7), 'R', self.game_manager, self, self.screen)
        self.w_bishop2 = Bishop(CHESS_PIECES_PATH + 'white-bishop.png', (5, 7), 'B', self.game_manager, self, self.screen)
        self.w_knight2 = Knight(CHESS_PIECES_PATH + 'white-knight.png', (6, 7), 'N', self.game_manager, self, self.screen)
        self.w_pawn1 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (0, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn2 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (1, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn3 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (2, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn4 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (3, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn5 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (4, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn6 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (5, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn7 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (6, 6), 'P', self.game_manager, self, self.screen)
        self.w_pawn8 = Pawn(CHESS_PIECES_PATH + 'white-pawn.png', (7, 6), 'P', self.game_manager, self, self.screen)

        self.b_king = King(CHESS_PIECES_PATH + 'black-king.png', (4, 0), 'k', self.game_manager, self, self.screen)
        self.b_queen = Queen(CHESS_PIECES_PATH + 'black-queen.png', (3, 0), 'q', self.game_manager, self, self.screen)
        self.b_rook1 = Rook(CHESS_PIECES_PATH + 'black-rook.png', (0, 0), 'r', self.game_manager, self, self.screen)
        self.b_bishop1 = Bishop(CHESS_PIECES_PATH + 'black-bishop.png', (2, 0), 'b', self.game_manager, self, self.screen)
        self.b_knight1 = Knight(CHESS_PIECES_PATH + 'black-knight.png', (1, 0), 'n', self.game_manager, self, self.screen)
        self.b_rook2 = Rook(CHESS_PIECES_PATH + 'black-rook.png', (7, 0), 'r', self.game_manager, self, self.screen)
        self.b_bishop2 = Bishop(CHESS_PIECES_PATH + 'black-bishop.png', (5, 0), 'b', self.game_manager, self, self.screen)
        self.b_knight2 = Knight(CHESS_PIECES_PATH + 'black-knight.png', (6, 0), 'n', self.game_manager, self, self.screen)
        self.b_pawn1 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (0, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn2 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (1, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn3 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (2, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn4 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (3, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn5 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (4, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn6 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (5, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn7 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (6, 1), 'p', self.game_manager, self, self.screen)
        self.b_pawn8 = Pawn(CHESS_PIECES_PATH + 'black-pawn.png', (7, 1), 'p', self.game_manager, self, self.screen)

    def import_fen(self, fen_string):
        rank = 0
        file = 0

        repeatable_pieces = {
            'r': [self.b_rook1, self.b_rook2],
            'n': [self.b_knight1, self.b_knight2],
            'b': [self.b_bishop1, self.b_bishop2],
            'p': [self.b_pawn1, self.b_pawn2, self.b_pawn3, self.b_pawn4, self.b_pawn5, self.b_pawn6, self.b_pawn7, self.b_pawn8],
            'R': [self.w_rook1, self.w_rook2],
            'N': [self.w_knight1, self.w_knight2],
            'B': [self.w_bishop1, self.w_bishop2],
            'P': [self.w_pawn1, self.w_pawn2, self.w_pawn3, self.w_pawn4, self.w_pawn5, self.w_pawn6, self.w_pawn7, self.w_pawn8]
        }

        single_pieces = {
            'q': self.b_queen,
            'k': self.b_king,
            'Q': self.w_queen,
            'K': self.w_king
        }

        self.pieces_list = []

        for c in fen_string.split()[0]:
            if c.isnumeric():
                file += int(c)
            elif c == '/':
                file = 0
                rank += 1
            else:
                if c in repeatable_pieces:
                    self.pieces_list.append(repeatable_pieces[c][0])
                    repeatable_pieces[c][0].update_position((file, rank))
                    repeatable_pieces[c].pop(0)
                elif c in single_pieces:
                    self.pieces_list.append(single_pieces[c])
                    single_pieces[c].update_position((file, rank))
                file += 1
            
        self.colour_to_move = fen_string.split()[1]
        self.game_manager.castle_info = fen_string.split()[2]
        self.game_manager.en_passant_target_square = fen_string.split()[3]
        self.game_manager.update_legal_moves()

    def generate_fen(self):
        fen = ''

        for rank in range(8):
            empty_squares = 0
            for file in range(8):
                found = False
                for piece in self.pieces_list:
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

        fen += ' b' if self.move_number % 2 else ' w'
        fen += ' ' + self.game_manager.castle_info
        fen += ' ' + self.game_manager.en_passant_target_square

        return fen

    def set_square_colour(self, square, colour=None):
        if not colour:
            square[0].fill(square[2])
            return
        
        square[0].fill(colour)

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
                pygame.draw.rect(self.screen, LEGAL_MOVE_HIGHLIGHT_COLOR, (x * SQUARE_SIZE + self.board_pos[0],
                                                                           y * SQUARE_SIZE + self.board_pos[1], 
                                                                           SQUARE_SIZE, SQUARE_SIZE), 10)

            center = (x * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_pos[0], 
                      y * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_pos[1])
            if self.get_piece_on_pos((x, y)):
                pygame.draw.circle(self.screen, LEGAL_MOVE_HIGHLIGHT_COLOR, center, SQUARE_SIZE // 2, 10)
            else:
                pygame.draw.circle(self.screen, LEGAL_MOVE_HIGHLIGHT_COLOR, center, 20)

    def update_move_squares(self):
        if self.move_squares:
            sq1, sq2 = [self.get_square(p) for p in self.move_squares]
            self.set_square_colour(sq1)
            self.set_square_colour(sq2)

        index = self.move_number - 1

        if index < 0:
            return

        self.move_squares = self.move_squares_list[index]
        sq1, sq2 = [self.get_square(p) for p in self.move_squares]
        self.set_square_colour(sq1, PREV_SQUARE_COLOR)
        self.set_square_colour(sq2, NEXT_SQUARE_COLOR)

    def get_positions_changed(self, prev_move_number, next_move_number):
        prev_0 = None
        next_0 = None
        prev_1 = None
        next_1 = None

        sq_list = [item for sublist in self.square_list for item in sublist]

        self.import_fen(self.moves_list[next_move_number])
        next_board_state = [self.get_piece_on_square(square) for square in sq_list]

        self.import_fen(self.moves_list[prev_move_number])
        prev_board_state = [self.get_piece_on_square(square) for square in sq_list]

        for i, square in enumerate(sq_list):
            prev_piece = prev_board_state[i]
            next_piece = next_board_state[i]

            if prev_piece is not None and next_piece is None:
                if prev_0: prev_1 = square
                else: prev_0 = square
            elif prev_piece is None and next_piece is not None:
                if next_0: next_1 = square
                else: next_0 = square
            elif prev_piece and next_piece and prev_piece.id != next_piece.id:
                if next_0: next_1 = square
                else: next_0 = square

        if not prev_1:
            return [prev_0, next_0]

        if next_1:
            if self.get_square_index(prev_0) == (0, 0):
                return [prev_1, prev_0, next_0, next_1]
            return [prev_0, prev_1, next_1, next_0]

        if self.get_square_index(prev_0)[0] < self.get_square_index(next_0)[0]:
            return [prev_0, next_0, prev_1]

        return [prev_1, next_0, prev_0] 

    def move_piece(self, start_square, end_square):
        start_index = self.get_square_index(start_square)
        end_index = self.get_square_index(end_square)

        piece = self.get_piece_on_square(start_square)
        piece.animate_move(start_index, end_index)

    def reset_board(self, user_color):
        self.user_colour = user_color
        if user_color == 'w':
            self.import_fen(START_POSITION_FEN_W)
            self.moves_list = [START_POSITION_FEN_W]
        else:
            self.import_fen(START_POSITION_FEN_B)
            self.moves_list = [START_POSITION_FEN_B]
        self.move_number = 0
        self.can_move = True
        self.update_move_squares()
        self.move_squares_list = []
        self.move_squares = []
        self.notations_list = []
    
    def undo(self):
        if self.move_number == len(self.moves_list) - 1 and self.move_number:
            self.move_number -= 1
            self.colour_to_move = 'b' if self.colour_to_move == 'w' else 'w'
            self.import_fen(self.moves_list[self.move_number])

            self.move_squares_list.pop()
            self.moves_list.pop()
            self.update_move_squares()
            self.state_manager.board_undo()

    def flip(self):
        self.user_colour = 'w' if self.user_colour == 'b' else 'b'
        fen = ''
        old_fen = self.generate_fen()
        fen = old_fen.split()[0][-2::-1] + ' ' + ' '.join(old_fen.split()[1:])
        
        self.import_fen(fen)
        self.game_manager.update_legal_moves()

    def get_algebraic_notation(self, piece, old_pos, new_pos, capture, check, castle):
        if castle:
            return castle + check

        piece_type = '' if piece.id.lower() == 'p' else piece.id.upper()
        
        destination = self.game_manager.index_to_chess_notation(new_pos)

        disambiguation = ''
        if piece_type:
            ambiguity = False
            for p in self.pieces_list:
                if p == piece or p.id != piece.id:
                    continue
                if new_pos in self.game_manager.legal_moves_dict[p]:
                    ambiguity = True
                    break

            if ambiguity:
                if p.get_position()[0] != old_pos[0]:
                    disambiguation = self.game_manager.index_to_chess_notation(old_pos)[0] 
                else:
                    disambiguation = self.game_manager.index_to_chess_notation(old_pos)[1] 

        elif capture:
            disambiguation = self.game_manager.index_to_chess_notation(old_pos)[0] 

        return piece_type + disambiguation + capture + destination + check

    def draw_board(self):
        pygame.draw.rect(self.screen, BUTTON_SHADOW_COLOR, self.rect, border_radius=0)

        for i in range(8):
            for j in range(8):
                square = self.square_list[i][j]
                self.screen.blit(square[0], square[1])

        self.highlight_possible_moves()

        for piece in self.pieces_list:
            piece.update_animation()
            piece.display()

    def handle_event(self, event):
        current_state = self.state_manager.get_state()
        if current_state is (AppState.MAIN_MENU or AppState.QUIT):
            return

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.can_move:
                    for piece in self.pieces_list:
                        if piece.rect.collidepoint(event.pos): 
                            if piece.colour != self.colour_to_move:
                                continue
                            Piece.picked = piece
                            piece.rect.center = event.pos
                            self.set_square_colour(piece.get_square(), PICKED_SQUARE_COLOR)
                            self.pieces_list.remove(piece)
                            self.pieces_list.append(piece)
                            self.possible_moves_list = self.game_manager.legal_moves_dict[piece]
                            break
            
        if event.type == MOUSEMOTION:
            if Piece.picked:
                Piece.picked.rect.center = event.pos
                found = False

                for pos in self.possible_moves_list:
                    sq = self.get_square(pos)
                    if sq[1].collidepoint(event.pos):
                        self.hover_pos = pos
                        found = True
                
                if not found:
                    self.hover_pos = None

        if event.type == MOUSEBUTTONUP:
            if Piece.picked and event.button == 1:
                self.set_square_colour(Piece.picked.get_square())

                index = self.square_centers.index(self.closest_point(Piece.picked.rect.center, self.square_centers))
                old_pos = Piece.picked.get_position()
                new_pos = index // 8, index % 8

                if new_pos not in self.possible_moves_list:
                    Piece.picked.update_position(old_pos)
                    Piece.picked = None
                    self.possible_moves_list = []
                    return
                
                capture = ''
                castle = ''
                piece = self.get_piece_on_pos(new_pos)
                if piece and piece.colour != self.colour_to_move: 
                    self.pieces_list.remove(piece) 
                    capture = 'x'
                elif piece and piece.colour == self.colour_to_move:
                    new_pos, castle = self.game_manager.castle(Piece.picked, piece)

                Piece.picked.update_position(new_pos)

                en_passant = self.game_manager.en_passant(Piece.picked, old_pos)
                capture = 'x' if en_passant else capture
                self.game_manager.update_castling_rights(Piece.picked, old_pos)

                piece = Piece.picked
                Piece.picked = None
                self.possible_moves_list = []
                self.hover_pos = None
                self.move_squares_list.append([old_pos, new_pos])
                self.move_number += 1
                self.update_move_squares()
                self.moves_list.append(self.generate_fen())
                self.colour_to_move = 'b' if self.colour_to_move == 'w' else 'w'
                check = self.game_manager.update_legal_moves()
                move_notation = self.get_algebraic_notation(piece, old_pos, new_pos, capture, check, castle)
                self.notations_list.append(move_notation)
                self.state_manager.move_made(move_notation)
                
        if event.type == KEYDOWN:
            if event.key == K_LCTRL:
                self.control_down = True

            if event.key == K_LEFT:
                if self.move_number > 0:
                    self.move_number -= 1  
                    self.import_fen(self.moves_list[self.move_number])

                    self.update_move_squares()

                if self.move_number != len(self.moves_list) - 1:
                    self.can_move = False

            elif event.key == K_RIGHT:
                if len(self.moves_list) > self.move_number + 1:
                    self.move_number += 1
                    self.import_fen(self.moves_list[self.move_number])

                    self.update_move_squares()

                if self.move_number == len(self.moves_list) - 1 :
                    self.can_move = True
            
            elif event.key == K_z and self.control_down:
                match self.state_manager.state:
                    case AppState.TRAINING:
                        pass
                    case _:
                        self.undo()

        if event.type == KEYUP:
            if event.key == K_LCTRL:
                self.control_down = False


class Piece:
    picked = None

    def __init__(self, image_location, position, id, game_manager, board, screen):
        self.screen = screen
        self.surf = pygame.image.load(image_location).convert_alpha()
        self.rect = self.surf.get_rect(topleft=(position[0] * SQUARE_SIZE, position[1] * SQUARE_SIZE))
        self.id = id
        self.colour = 'w' if self.id.isupper() else 'b'
        self.position = position
        self.board = board
        self.game_manager = game_manager
        self.board.pieces_pos_list[position[0]][position[1]] = self
        self.board.pieces_list.append(self)
        self.animating = False
        self.time = 0
        self.duration = MOVE_ANIMATION_DURATION
        self.update_position(self.position)

    def update_position(self, position):
        self.position = position
        self.rect.topleft = (self.position[0] * SQUARE_SIZE + self.board.board_pos[0], self.position[1] * SQUARE_SIZE + self.board.board_pos[1]) 
        self.rect.center = self.board.closest_point(self.rect.center, self.board.square_centers)

    def get_position(self):
        return self.position

    def get_square(self):
        return self.board.square_list[self.position[0]][self.position[1]]

    def display(self):
        self.screen.blit(self.surf, self.rect)

    def ease_in_out(self, t):
        if t < 0.5:
            return 8 * t ** 4
        else:
            return 1 - 8 * (1 - t) ** 4

    def animate_move(self, start_pos, end_pos):
        start_point = (start_pos[0] * SQUARE_SIZE + self.board.board_pos[0], start_pos[1] * SQUARE_SIZE + self.board.board_pos[1]) 
        end_point = (end_pos[0] * SQUARE_SIZE + self.board.board_pos[0], end_pos[1] * SQUARE_SIZE + self.board.board_pos[1])
        self.start_pos = self.board.closest_point(start_point, self.board.square_centers)
        self.end_pos = self.board.closest_point(end_point, self.board.square_centers)
        self.board.pieces_list.remove(self)
        self.board.pieces_list.append(self)
        self.animating = True
        self.time = 0

    def update_animation(self):
        if self.animating:
            t = self.time / self.duration
            t = self.ease_in_out(t)
            if t >= 1:
                t = 1
                self.animating = False
                self.update_position((self.end_pos[0] // SQUARE_SIZE, self.end_pos[1] // SQUARE_SIZE))
                fen = self.board.moves_list[self.board.move_number]
                self.board.colour_to_move = fen.split()[1]
                self.game_manager.castle_info = fen.split()[2]
                self.game_manager.en_passant_target_square = fen.split()[3]
                self.game_manager.update_legal_moves()
                return

            self.rect.center = (
                self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t,
                self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
            )
            self.time += 1


class King(Piece):
    def generate_moves(self, only_attack_moves=False):
        move_offsets = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        possible_moves = []

        for i in [0, 7]:
            pos = (i, self.get_position()[1])
            rook = self.board.get_piece_on_pos(pos)
            if rook and rook.id.lower() == 'r' and rook.colour == self.colour:
                if self.game_manager.can_castle(self, rook):
                    possible_moves.append(pos)
                
        for offset in move_offsets:
            x, y = self.get_position()
            x += offset[0]
            y += offset[1]

            if 0 <= x < 8 and 0 <= y < 8:
                target_square = self.board.get_square((x, y))
                piece = self.board.get_piece_on_square(target_square)
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
                    target_square = self.board.get_square((x, y))
                    piece = self.board.get_piece_on_square(target_square)
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
                target_square = self.board.get_square((x, y))
                piece = self.board.get_piece_on_square(target_square)
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
                    target_square = self.board.get_square((x, y))
                    piece = self.board.get_piece_on_square(target_square)
                    if not piece:
                        possible_moves.append((x, y))
                    else:
                        if piece.colour != self.colour:
                            possible_moves.append((x, y))
                        break
                else:
                    break

        return possible_moves


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
                    target_square = self.board.get_square((x, y))
                    piece = self.board.get_piece_on_square(target_square)
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
        if self.colour == self.board.user_colour:
            move_offsets = [(0, -1), (0, -2), (1, -1), (-1, -1)]
            initial_y = 6
        else:
            move_offsets = [(0, 1), (0, 2), (1, 1), (-1, 1)]
            initial_y = 1

        possible_moves = []

        for offset in move_offsets:
            x, y = self.get_position()
            x += offset[0]
            y += offset[1]

            if not (0 <= x < 8 and 0 <= y < 8):
                continue

            # En passant 
            if abs(offset[0]) == 1:
                if self.game_manager.en_passant_target_square == self.game_manager.index_to_chess_notation((x, y)):
                    possible_moves.append((x, y))
                    continue

            if only_attack_moves:
                # Remove forward_moves
                if offset[0] == 0:
                    continue

                possible_moves.append((x, y))

            else:
                # Initial two square move
                if abs(offset[1]) == 2:
                    x, y = self.get_position()
                    if y != initial_y:
                        continue

                    sq1 = self.board.get_square((x, y + move_offsets[0][1]))
                    sq2 = self.board.get_square((x, y + offset[1]))
                    if not (self.board.get_piece_on_square(sq1) or self.board.get_piece_on_square(sq2)):
                        possible_moves.append((x, y + offset[1]))
                    continue

                target_square = self.board.get_square((x, y))
                piece = self.board.get_piece_on_square(target_square)
                if not piece and offset[0] == 0:
                    possible_moves.append((x, y))
                elif piece and offset[0] != 0:
                    if piece.colour != self.colour:
                        possible_moves.append((x, y))

        return possible_moves
