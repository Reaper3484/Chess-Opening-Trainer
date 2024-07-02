import json
from constants import *
from datetime import datetime, timedelta


class Trainer:
    def __init__(self) -> None:
        self.board = None
        self.opening_data = self.load_opening_data()
        self.today_training_batch = self.get_training_batch()
        self.is_training = False
        pass

    def initialize_dependencies(self, board):
        self.board = board

    def load_opening_data(self):
        data = {}
        with open('opening_data.json') as file:
            data = json.load(file) 
            return data

    def get_training_batch(self):
        batch = []
        today = str(datetime.date(datetime.today()))
        for opening in self.opening_data['openings']:
            if opening['next_review'] == today:
                batch.append(opening)
        return batch

    def calculate_next_review_date(self, interval):
        today = datetime.now()
        next_review = today + timedelta(days=interval)
        return next_review.strftime('%d-%m-%Y')

    def train_next(self):
        if self.today_training_batch:
            self.is_training = True
            opening = self.today_training_batch.pop(0)
            self.start_training(opening)
            return opening['name']

        self.is_training = False
        return 'Finished!'

    def start_training(self, opening):
        self.board.reset_board()
        self.moves_list = opening['moves_list']
        self.ai_color = opening['ai_color']
        if self.ai_color == 'w':
            self.board.user_colour = 'b'
            self.board.import_fen(START_POSITION_FEN_B)
            self.board.moves_list = [START_POSITION_FEN_B]
            self.make_move()

    def make_move(self):
        fen = self.moves_list[self.board.move_number]
        self.board.move_number += 1
        self.board.moves_list.append(fen)

        if self.board.move_number == len(self.moves_list):
            self.is_training = False

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
    
    def show_correct_move(self):
        fen = self.moves_list[self.board.move_number]
        number = self.board.move_number
        self.board.moves_list.append(fen)

        squares = self.board.get_positions_changed(number, number + 1)
        sq1, sq2 = squares
        self.board.set_square_colour(sq1, PREV_CORRECT_SQUARE_COLOR)
        self.board.set_square_colour(sq2, NEXT_CORRECT_SQUARE_COLOR)
        self.board.moves_list.pop()
    
    def move(self):
        user_move = self.board.moves_list[self.board.move_number]
        correct_move = self.moves_list[self.board.move_number - 1]
        if user_move == correct_move:
            self.make_move()
            return

        self.board.undo()
        self.show_correct_move()