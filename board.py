import pygame


class Board:
    def __init__(self):
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
        self.initialise_board()

    def initialise_board(self):
        for i in range(8):
            for j in range(8):
                square_surf = pygame.Surface((square_size, square_size))
                square_rect = square_surf.get_rect(topleft = (i * square_size, j * square_size))
                self.square_centers.append(square_rect.center)
                if ((i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1)):
                    square_surf.fill(light_square_color)
                    self.square_list[i][j] = (square_surf, square_rect, light_square_color)
                else:
                    square_surf.fill(dark_square_color)
                    self.square_list[i][j] = (square_surf, square_rect, dark_square_color)

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
                pygame.draw.rect(screen, 'grey', (x * square_size, y * square_size, square_size, square_size), 10)

            center = (x * square_size + square_size // 2, y * square_size + square_size // 2)
            if self.get_piece_on_pos((x, y)):
                pygame.draw.circle(screen, 'grey', center, square_size // 2, 10)
            else:
                pygame.draw.circle(screen, 'grey', center, 20)

    def update_move_squares(self):
        if self.move_squares:
            sq1, sq2 = [board.get_square(p) for p in self.move_squares]
            board.set_square_colour(sq1)
            board.set_square_colour(sq2)

        index = board.move_number - 1

        if index < 0:
            return

        self.move_squares = self.move_squares_list[index]
        sq1, sq2 = [board.get_square(p) for p in self.move_squares_list[index]]
        board.set_square_colour(sq1, prev_square_color)
        board.set_square_colour(sq2, next_square_color)

    def get_positions_changed(self, prev_move_number, next_move_number):
        prev_0 = None
        next_0 = None
        prev_1 = None
        next_1 = None

        sq_list = [item for sublist in board.square_list for item in sublist]

        import_fen(board.moves_list[next_move_number])
        next_board_state = [board.get_piece_on_square(square) for square in sq_list]

        import_fen(board.moves_list[prev_move_number])
        prev_board_state = [board.get_piece_on_square(square) for square in sq_list]

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

    def draw_board(self):
        for i in range(8):
            for j in range(8):
                square = self.square_list[i][j]
                screen.blit(square[0], square[1])

        self.highlight_possible_moves()

        for piece in self.pieces_list:
            piece.update_animation()
            piece.display()


class Piece:
    picked = None

    def __init__(self, image_location, position, id):
        self.surf = pygame.image.load(image_location).convert_alpha()
        self.rect = self.surf.get_rect(topleft=(position[0] * square_size, position[1] * square_size))
        self.id = id
        self.colour = 'w' if self.id.isupper() else 'b'
        self.position = position
        board.pieces_pos_list[position[0]][position[1]] = self
        board.pieces_list.append(self)
        self.animating = False
        self.time = 0
        self.duration = 20
        self.update_position(self.position)

    def update_position(self, position):
        self.position = position
        self.rect.topleft = (self.position[0] * square_size, self.position[1] * square_size)
        self.rect.center = board.closest_point(self.rect.center, board.square_centers)

    def get_position(self):
        return self.position

    def get_square(self):
        return board.square_list[self.position[0]][self.position[1]]

    def display(self):
        screen.blit(self.surf, self.rect)

    def ease_in_out(self, t):
        if t < 0.5:
            return 8 * t ** 4
        else:
            return 1 - 8 * (1 - t) ** 4

    def animate_move(self, start_pos, end_pos):
        self.start_pos = (start_pos[0] * square_size, start_pos[1] * square_size)
        self.end_pos = (end_pos[0] * square_size, end_pos[1] * square_size)
        board.pieces_list.remove(self)
        board.pieces_list.append(self)
        self.animating = True
        self.time = 0

    def update_animation(self):
        if self.animating:
            t = self.time / self.duration
            t = self.ease_in_out(t)
            if t >= 1:
                t = 1
                self.animating = False
                self.update_position((self.end_pos[0] // square_size, self.end_pos[1] // square_size))
                fen = board.moves_list[board.move_number]
                board.colour_to_move = fen.split()[1]
                game_manager.castle_info = fen.split()[2]
                game_manager.en_passant_target_square = fen.split()[3]
                ui.refresh()
                game_manager.update_legal_moves()
                return

            self.rect.topleft = (
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
            rook = board.get_piece_on_pos(pos)
            if rook and rook.id.lower() == 'r' and rook.colour == self.colour:
                if game_manager.can_castle(self, rook):
                    possible_moves.append(pos)
                
        for offset in move_offsets:
            x, y = self.get_position()
            x += offset[0]
            y += offset[1]

            if 0 <= x < 8 and 0 <= y < 8:
                target_square = board.get_square((x, y))
                piece = board.get_piece_on_square(target_square)
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
                    target_square = board.get_square((x, y))
                    piece = board.get_piece_on_square(target_square)
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
                target_square = board.get_square((x, y))
                piece = board.get_piece_on_square(target_square)
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
                    target_square = board.get_square((x, y))
                    piece = board.get_piece_on_square(target_square)
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
                    target_square = board.get_square((x, y))
                    piece = board.get_piece_on_square(target_square)
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
        if self.colour == board.user_colour:
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
                if game_manager.en_passant_target_square == game_manager.index_to_chess_notation((x, y)):
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

                    sq1 = board.get_square((x, y + move_offsets[0][1]))
                    sq2 = board.get_square((x, y + offset[1]))
                    if not (board.get_piece_on_square(sq1) or board.get_piece_on_square(sq2)):
                        possible_moves.append((x, y + offset[1]))
                    continue

                target_square = board.get_square((x, y))
                piece = board.get_piece_on_square(target_square)
                if not piece and offset[0] == 0:
                    possible_moves.append((x, y))
                elif piece and offset[0] != 0:
                    if piece.colour != self.colour:
                        possible_moves.append((x, y))

        return possible_moves
