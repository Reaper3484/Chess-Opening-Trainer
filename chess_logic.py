class GameManager:
    def __init__(self, board, state_manager):
        self.board = board
        self.state_manager = state_manager
        self.en_passant_target_square = '-'
        self.castle_info = 'KQkq'
        self.castling_in_progress = False
        self.legal_moves_dict = {}

    def index_to_chess_notation(self, index):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        if self.board.user_colour == 'b':
            files = files[::-1]
            ranks = ranks[::-1]

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
        for piece in self.board.pieces_list:
            if piece.colour != king.colour:
                attack_moves = piece.generate_moves(only_attack_moves=True)
                if king_position in attack_moves:
                    return True
        return False

    def update_legal_moves(self):
        for piece in self.board.pieces_list:
            if piece.id.lower() == 'k' and piece.colour == self.board.colour_to_move:
                king = piece

        no_legal_moves = True
        for piece in self.board.pieces_list.copy():
            if piece.colour == self.board.colour_to_move:
                legal_moves = []
                possible_moves = piece.generate_moves()
                old_pos = piece.get_position()

                for move in possible_moves:
                    enemy_piece = self.board.get_piece_on_pos(move)
                    if enemy_piece and enemy_piece.colour != self.board.colour_to_move:
                        self.board.pieces_list.remove(enemy_piece)
                    piece.update_position(move) 

                    if not self.is_king_in_check(king):
                       legal_moves.append(move) 

                    piece.update_position(old_pos)
                    if enemy_piece:
                        self.board.pieces_list.append(enemy_piece)

                self.legal_moves_dict[piece] = legal_moves
                if legal_moves:
                    no_legal_moves = False

        check = False
        if self.is_king_in_check(king):
            check = True

        if no_legal_moves:
            if check:
                return '#'
            else:
                return '1/2'

        if check:
            return '+'

        return ''

    def en_passant(self, pawn, old_pos):
        new_pos = pawn.get_position()

        if pawn.id.lower() == 'p' and self.en_passant_target_square != '-':
            target_index = self.chess_notation_to_index(self.en_passant_target_square)
            if new_pos == target_index:
                captured_pawn = self.board.get_piece_on_pos((new_pos[0], old_pos[1]))
                self.board.pieces_list.remove(captured_pawn)
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

        if self.board.user_colour == 'w':
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
            if self.board.get_piece_on_pos(sq):
                return False

        # Check if path is attacked
        self.castling_in_progress = True
        for piece in self.board.pieces_list:
            if piece.colour != king.colour:
                attack_positions = piece.generate_moves(only_attack_moves=True)
                for pos in attack_positions:
                    if pos in path or pos == king_pos:
                        self.castling_in_progress = False
                        return False

        self.castling_in_progress = False

        if self.board.user_colour == 'w':
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

        castle = 'O-O' if abs(rook_pos[0] - new_rook_pos[0]) == 2 else 'O-O-O'
        return new_king_pos, castle
