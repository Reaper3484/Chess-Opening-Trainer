


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
