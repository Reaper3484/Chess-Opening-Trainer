import pygame


class UI:
    def __init__(self):
        font = pygame.font.Font(None, 90)
        self.train_text_surf = font.render('Train', True, '#231f20')
        self.train_text_rect = self.train_text_surf.get_rect(topleft=(9 * square_size, 4 * square_size + square_size/16))

        self.learn_text_surf = font.render('Learn', True, '#231f20')
        self.learn_text_rect = self.learn_text_surf.get_rect(topleft=(9 * square_size, 5 * square_size + square_size/16))

        self.image = pygame.image.load('graphics/flip_icon.png').convert_alpha()
        self.flip_button_surf = pygame.transform.scale(self.image, (square_size - 40, square_size - 40))
        self.flip_button_rect = self.flip_button_surf.get_rect(center=(9 * square_size + self.learn_text_rect.size[0]//2, 6 * square_size + square_size/16))

        self.can_press_learn = True

    def draw(self):
        pygame.draw.rect(screen, 'white', self.train_text_rect, border_radius=5)
        screen.blit(self.train_text_surf, self.train_text_rect)

        if self.can_press_learn:
            pygame.draw.rect(screen, 'white', self.learn_text_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, 'dark grey', self.learn_text_rect, border_radius=5)
        screen.blit(self.learn_text_surf, self.learn_text_rect)

        pygame.draw.rect(screen, 'white', self.flip_button_rect, border_radius=5)
        screen.blit(self.flip_button_surf, self.flip_button_rect)

    def refresh(self):
        if board.user_colour == 'w' and board.colour_to_move == 'w':
            self.can_press_learn = True
        elif board.user_colour == 'b' and board.colour_to_move == 'b':
            self.can_press_learn = True
        else:
            self.can_press_learn = False

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
