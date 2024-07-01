import pygame
from pygame.locals import *
from constants import *
from board import Piece


class EventHandler:
    def __init__(self) -> None:
        self.board = None
        self.ui_manager = None
        self.game_manager = None
        self.ai = None
        self.state_manager = None

    def initialize_dependencies(self, board, ui_manager, ai, game_manager):
        self.board = board
        self.ui_manager = ui_manager
        self.game_manager = game_manager
        self.ai = ai
        # self.state_manager = 
        
    def handle_board_events(self, event):
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
                
                piece = self.get_piece_on_pos(new_pos)
                if piece and piece.colour != self.colour_to_move: 
                    self.pieces_list.remove(piece) 
                elif piece and piece.colour == self.colour_to_move:
                    new_pos = self.game_manager.castle(Piece.picked, piece)

                Piece.picked.update_position(new_pos)

                self.game_manager.en_passant(Piece.picked, old_pos)
                self.game_manager.update_castling_rights(Piece.picked, old_pos)

                Piece.picked = None
                self.possible_moves_list = []
                self.hover_pos = None
                self.move_squares_list.append([old_pos, new_pos])
                self.move_number += 1
                self.update_move_squares()
                self.board.moves_list.append(self.board.generate_fen())
                self.board.colour_to_move = 'b' if self.board.colour_to_move == 'w' else 'w'

                if self.ai.is_training:
                    self.ai.move()
                else:
                    self.ui_manager.refresh()
                    self.game_manager.update_legal_moves()
                
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                if self.board.move_number > 0:
                    self.board.move_number -= 1  
                    self.board.import_fen(self.board.moves_list[self.board.move_number])

                    self.board.update_move_squares()

                if self.board.move_number != len(self.board.moves_list) - 1:
                    self.board.can_move = False

            elif event.key == K_RIGHT:
                if len(self.board.moves_list) > self.board.move_number + 1:
                    self.board.move_number += 1
                    self.board.import_fen(self.board.moves_list[self.board.move_number])

                    self.board.update_move_squares()

                if self.board.move_number == len(self.board.moves_list) - 1 :
                    self.board.can_move = True
            
            elif event.key == K_z:
                if self.board.move_number == len(self.board.moves_list) - 1 and self.board.move_number:
                    self.board.move_number -= 1
                    self.board.colour_to_move = 'b' if self.board.colour_to_move == 'w' else 'w'
                    self.board.import_fen(self.board.moves_list[self.board.move_number])

                    self.board.move_squares_list.pop()
                    self.board.moves_list.pop()
                    self.board.update_move_squares()
                    self.ui_manager.refresh()
                    self.game_manager.update_legal_moves()
            
            elif event.key == K_f:
                print(self.board.generate_fen())
