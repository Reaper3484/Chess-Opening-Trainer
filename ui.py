import pygame
import json
from constants import *

class Button:
    def __init__(self, text, callback, center, size):
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, FONT_SIZE)

    def draw(self, screen):
        pygame.draw.rect(screen, 'white', self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, FONT_COLOR)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height= self.screen.get_width(), self.screen.get_height()
        self.board = None
        self.ai = None
        self.game_manager = None
        self.state_manager = None

        font = pygame.font.Font(FONT, FONT_SIZE)
        self.train_text_surf = font.render('Train', True, FONT_COLOR)
        self.train_text_rect = self.train_text_surf.get_rect(topleft=(9 * SQUARE_SIZE, 4 * SQUARE_SIZE + SQUARE_SIZE/16))

        self.learn_text_surf = font.render('Learn', True, FONT_COLOR)
        self.learn_text_rect = self.learn_text_surf.get_rect(topleft=(9 * SQUARE_SIZE, 5 * SQUARE_SIZE + SQUARE_SIZE/16))

        self.image = pygame.image.load(IMAGE_PATH + 'flip_icon.png').convert_alpha()
        self.flip_button_surf = pygame.transform.scale(self.image, (SQUARE_SIZE - 40, SQUARE_SIZE - 40))
        self.flip_button_rect = self.flip_button_surf.get_rect(center=(9 * SQUARE_SIZE + self.learn_text_rect.size[0]//2, 6 * SQUARE_SIZE + SQUARE_SIZE/16))

        self.can_press_learn = True

        self.main_menu_buttons = [
            Button('Train Today', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 - 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Add Opening', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 - 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Practice', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 + 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Settings', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 + 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
        ]
    
    def initialize_dependencies(self, board, ai, game_manager, state_manager):
        self.board = board
        self.ai = ai
        self.game_manager = game_manager
        self.state_manager = state_manager

    def handle_event(self, event):
        for button in self.main_menu_buttons:
            button.handle_event(event)

    def draw(self):
        pygame.draw.rect(self.screen, 'white', self.train_text_rect, border_radius=5)
        self.screen.blit(self.train_text_surf, self.train_text_rect)

        if self.can_press_learn:
            pygame.draw.rect(self.screen, 'white', self.learn_text_rect, border_radius=5)
        else:
            pygame.draw.rect(self.screen, 'dark grey', self.learn_text_rect, border_radius=5)
        self.screen.blit(self.learn_text_surf, self.learn_text_rect)

        pygame.draw.rect(self.screen, 'white', self.flip_button_rect, border_radius=5)
        self.screen.blit(self.flip_button_surf, self.flip_button_rect)

        for button in self.main_menu_buttons:
            button.draw(self.screen)

    def refresh(self):
        if self.board.user_colour == 'w' and self.board.colour_to_move == 'w':
            self.can_press_learn = True
        elif self.board.user_colour == 'b' and self.board.colour_to_move == 'b':
            self.can_press_learn = True
        else:
            self.can_press_learn = False

    def train(self):
        with open('data.json', 'r') as file:
            self.ai.data = json.load(file)

        self.ai.is_training = True if not self.ai.is_training else False
        print('training started' if self.ai.is_training else 'training stopped')
        self.ai.move()

    def flip(self):
        self.board.user_colour = 'w' if self.board.user_colour == 'b' else 'b'
        fen = ''
        old_fen = self.board.generate_fen()
        fen = old_fen.split()[0][-2::-1] + ' ' + ' '.join(old_fen.split()[1:])
        
        self.board.import_fen(fen)
        self.game_manager.update_legal_moves()
        self.refresh()

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
