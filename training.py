import json
from constants import *


class Trainer:
    def __init__(self) -> None:
        self.ai = None
        self.opening_data = self.load_opening_data()
        self.today_training_batch = self.get_training_batch()
        pass

    def initialize_dependencies(self, ai):
        self.ai = ai

    def load_opening_data(self):
        data = {}
        with open('opening_data.json') as file:
            data = json.load(file) 
            return data

    def get_training_batch(self):
        batch = []
        for opening in self.opening_data.items():
            batch.append(opening)
        return batch

    def train_next(self):
        if self.today_training_batch:
            name, info = self.today_training_batch.pop(0)
            data = info['moves_list']
            ai_color = info['ai_color']
            self.ai.start_training(data, ai_color)
            return name


class AI2:
    def __init__(self):
        self.board = None
        self.game_manager = None
        self.is_learning = False
        self.is_training = False
        self.start_move = 0
        self.end_move = 0
        self.ai_color = None
        self.last_move = None
        self.temp = ''
        self.data = {}
                
    def initialize_dependencies(self, board, game_manager):
        self.board = board
        self.game_manager = game_manager

    def start_training(self, data, ai_color):
        self.board.reset_board()
        self.data = data
        self.ai_color = ai_color
        self.last_move = list(data.items())[-1][0]
        self.is_training = True

    def move(self):
        if self.ai_color == 'b':
            pass

        fen = self.board.moves_list[self.board.move_number]
        if fen == self.last_move:
            self.is_training = False
        fen = self.data[fen]
        self.board.moves_list.append(fen)
        self.board.move_number += 1

        squares = self.board.get_positions_changed(self.board.move_number - 1, self.board.move_number)
        if len(squares) == 4:
            self.board.move_piece(squares[0], squares[2])
            self.board.move_piece(squares[1], squares[3])
        elif len(squares) == 3:
            self.board.move_piece(squares[0], squares[1])
            self.board.pieces_list.remove(self.board.get_piece_on_square(squares[2]))
        else:
            self.board.move_piece(squares[0], squares[1])
            piece = self.board.get_piece_on_square(squares[1])
            if piece: self.board.pieces_list.remove(piece)

        self.board.move_squares_list.append([self.board.get_square_index(squares[0]), self.board.get_square_index(squares[1])])
        self.board.update_move_squares()

    def learn(self):
        for i in range(self.start_move, self.end_move, 2):
            if i + 1 < len(self.board.moves_list):
                if self.board.user_colour == 'w': 
                    white_move_fen = self.board.moves_list[i]
                    black_move_fen = self.board.moves_list[i + 1]
                    self.data['b'][white_move_fen] = black_move_fen
                else:
                    black_move_fen = self.board.moves_list[i]
                    white_move_fen = self.board.moves_list[i + 1]
                    self.data['w'][black_move_fen] = white_move_fen


class AI:
    def __init__(self):
        self.board = None
        self.game_manager = None
        self.is_learning = False
        self.is_training = False
        self.start_move = 0
        self.end_move = 0
        self.temp = ''
        self.data = {"AI as black": {},
                     "AI as white": {}}
                
    def initialize_dependencies(self, board, game_manager):
        self.board = board
        self.game_manager = game_manager

    def move(self):
        ai_colour = 'b' if self.board.user_colour == 'w' else 'w'
        fen = self.data[ai_colour][self.board.generate_fen()]
        self.board.moves_list.append(fen)
        self.board.move_number += 1

        squares = self.board.get_positions_changed(self.board.move_number - 1, self.board.move_number)
        if len(squares) == 4:
            self.game_manager.move_piece(squares[0], squares[2])
            self.game_manager.move_piece(squares[1], squares[3])
        elif len(squares) == 3:
            self.game_manager.move_piece(squares[0], squares[1])
            self.board.pieces_list.remove(self.board.get_piece_on_square(squares[2]))
        else:
            self.game_manager.move_piece(squares[0], squares[1])
            piece = self.board.get_piece_on_square(squares[1])
            if piece: self.board.pieces_list.remove(piece)

        self.board.move_squares_list.append([self.board.get_square_index(squares[0]), self.board.get_square_index(squares[1])])
        self.board.update_move_squares()

    def learn(self):
        for i in range(self.start_move, self.end_move, 2):
            if i + 1 < len(self.board.moves_list):
                if self.board.user_colour == 'w': 
                    white_move_fen = self.board.moves_list[i]
                    black_move_fen = self.board.moves_list[i + 1]
                    self.data['b'][white_move_fen] = black_move_fen
                else:
                    black_move_fen = self.board.moves_list[i]
                    white_move_fen = self.board.moves_list[i + 1]
                    self.data['w'][black_move_fen] = white_move_fen
