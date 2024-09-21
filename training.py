import json
from config import *
from datetime import datetime, timedelta
from board import Board


class Trainer:
    def __init__(self, screen, state_manager) -> None:
        self.scheduler = Scheduler()
        self.board = Board(screen, state_manager)
        self.state_manager = state_manager
        self.opening_data = self.load_opening_data()
        self.today_training_batch = self.scheduler.get_training_batch(self.opening_data['openings'])
        self.is_training_batch_finished = True
        self.modified_squares = []

    def load_opening_data(self):
        data = {}
        with open(DATA_FILE, 'r') as file:
            data = json.load(file) 
            return data

    def save_data(self):
        with open(DATA_FILE, 'w') as file:
            json.dump(self.opening_data, file, indent=4)

    def add_new_opening(self, name, color, moves, notations):
        new_opening = {
            "name": name,
            "user_color": color,
            "moves_list": moves,
            "notations_list" :notations,
            "next_review": self.scheduler.next_review_datetime(minutes=LEARNING_STEPS[0]),
            "interval": 1,
            "ease": 2.5,
            "current_step": 0,
            "type": "learning"
        }

        self.opening_data["openings"].append(new_opening)
        self.opening_data["openings"].sort(key=lambda x: x["next_review"])
        self.save_data()
        self.today_training_batch = self.scheduler.get_training_batch(self.opening_data['openings'])

    def train_next(self):
        if self.today_training_batch:
            self.is_training_batch_finished = False
            opening = self.today_training_batch.pop(0)
            self.moves_list = opening['moves_list']
            self.notations_list = opening['notations_list']
            self.user_color = opening['user_color']
            self.board.reset_board(self.user_color)
            self.moves_list = self.moves_list.copy()
            self.board.import_fen(self.moves_list.pop(0))
            self.current_opening = opening
            if self.user_color == 'b':
                self.make_move()

            return opening['name']

        self.training_batch_finished = True
        return 'Finished!'

    def make_move(self):
        fen = self.moves_list[self.board.move_number]
        self.board.move_number += 1
        self.board.moves_list.append(fen)

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
        self.state_manager.add_trainer_move(self.notations_list[self.board.move_number - 1])
        self.board.update_move_squares()
    
    def show_correct_move(self):
        fen = self.moves_list[self.board.move_number]
        number = self.board.move_number
        self.board.moves_list.append(fen)

        squares = self.board.get_positions_changed(number, number + 1)
        sq1, sq2 = self.modified_squares = squares[:2]
        self.board.set_square_colour(sq1, PREV_CORRECT_SQUARE_COLOR)
        self.board.set_square_colour(sq2, NEXT_CORRECT_SQUARE_COLOR)
        self.board.moves_list.pop()
    
    def submit_user_response(self, response):
        self.scheduler.update_srs_parameters(self.current_opening, response)
        self.scheduler.schedule_opening(self.current_opening, self.today_training_batch)
        self.save_data()
    
    def revert_modified_squares(self):
        for sq in self.modified_squares:
            self.board.set_square_colour(sq)

    def train(self):
        self.revert_modified_squares()
        user_move = self.board.moves_list[self.board.move_number]
        correct_move = self.moves_list[self.board.move_number - 1]
        if user_move == correct_move:
            if self.board.move_number == len(self.moves_list):
                self.board.can_move = False
                self.state_manager.get_user_response()
                return

            self.make_move()
            if self.board.move_number == len(self.moves_list):
                self.board.can_move = False
                self.state_manager.get_user_response()
            return

        self.board.undo()
        self.show_correct_move()


class Scheduler:
    def get_training_batch(self, openings):
        today = self.get_today_datetime()
        due_openings = [o for o in openings if o["next_review"] <= today]
        return sorted(due_openings, key=lambda x: x["next_review"])

    def schedule_opening(self, opening, queue):
        today = self.get_today_datetime()
        if opening["next_review"] <= today:
            queue.append(opening)
            queue.sort(key=lambda x: x["next_review"])  

    def next_review_datetime(self, days=0, minutes=0):
        next_review = datetime.now() + timedelta(days=days, minutes=minutes)
        return next_review.strftime("%Y-%m-%dT%H:%M:%S")
    
    def get_today_datetime(self):
        return (datetime.now() + timedelta(minutes=LEARN_AHEAD_TIME)).strftime("%Y-%m-%dT%H:%M:%S")

    def update_srs_parameters(self, opening, response):
        if opening["type"] == "learning":
            self.update_learning_parameters(opening, response)
        elif opening["type"] == "relearning":
            self.update_relearning_parameters(opening, response)
        elif opening["type"] == "review":
            self.update_review_parameters(opening, response)

    def update_learning_parameters(self, opening, response):
        if response == "Again":
            opening["current_step"] = 0
        elif response == "Good":
            opening["current_step"] += 1
        
        if opening["current_step"] < len(LEARNING_STEPS):
            interval = LEARNING_STEPS[opening["current_step"]]
            opening["next_review"] = self.next_review_datetime(minutes=interval)
        else:
            opening["type"] = "review"
            opening["interval"] = 1
            opening["next_review"] = self.next_review_datetime(days=1)

    def update_relearning_parameters(self, opening, response):
        if response == "Again":
            opening["current_step"] = 0
        elif response == "Good":
            opening["current_step"] += 1
        
        if opening["current_step"] < len(LEARNING_STEPS):
            interval = LEARNING_STEPS[opening["current_step"]]
            opening["next_review"] = self.next_review_datetime(minutes=interval)
        else:
            opening["type"] = "review"
            opening["next_review"] = self.next_review_datetime(days=opening["interval"])

    def update_review_parameters(self, opening, response):
        if response == "Again":
            opening["type"] = "relearning"
            opening["ease"] = max(1.3, opening["ease"] - 0.2)
            opening["interval"] *= NEW_INTERVAL_FACTOR
            opening["current_step"] = 0
            opening["next_review"] = self.next_review_datetime(minutes=LEARNING_STEPS[0])
        elif response == "Hard":
            opening["ease"] = max(1.3, opening["ease"] - 0.15)
            opening["interval"] *= HARD_INTERVAL_FACTOR
            opening["next_review"] = self.next_review_datetime(days=opening["interval"])
        elif response == "Good":
            opening["interval"] *= opening["ease"]
            opening["next_review"] = self.next_review_datetime(days=opening["interval"])

