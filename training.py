class AI:
    def __init__(self):
        self.board = None
        self.game_maanger = None
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
