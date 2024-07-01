import json


class DataManager:
    def __init__(self, board, ai, game_manager, ui) -> None:
        self.board = board
        self.game_manager = game_manager
        self.ui = ui
        self.ai = ai

    def train(self):
        with open('data.json', 'r') as file:
            self.ai.data = json.load(file)

        self.ai.is_training = True if not self.ai.is_training else False
        print('training started' if self.ai.is_training else 'training stopped')
        self.ai.move()

    def learn(self):
        if not self.ai.is_learning:
            print('learning')
            self.ai.is_learning = True
            if self.board.user_colour == 'w':
                self.ai.start_move = self.board.move_number + 1

            with open('data.json', 'r') as file:
                self.ai.data = json.load(file)

        else:
            print('finished')
            self.ai.is_learning = False
            self.ai.end_move = self.board.move_number
            self.ai.learn()
            with open('data.json', 'w') as file:
                json.dump(self.ai.data, file, indent=4)
