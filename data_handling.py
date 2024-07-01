import json


class DataManager:
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
