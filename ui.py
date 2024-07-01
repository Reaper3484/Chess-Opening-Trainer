import pygame
from  pygame.locals import *
from constants import *
import json
from state_manager import AppState

class Button:
    def __init__(self, text, callback, center, size):
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.text = text
        self.callback = callback
        self.color = BUTTON_COLOR
        self.hover = False
        self.font = pygame.font.Font(FONT, FONT_SIZE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        text_surface = self.font.render(self.text, True, FONT_COLOR)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
            self.color = BUTTON_COLOR
        elif event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos): 
                self.color = BUTTON_HOVER_COLOR
            else:
                self.color = BUTTON_COLOR
            

class IconButton:
    def __init__(self, image_path, callback, center, size):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image_surf = pygame.transform.scale(self.image, size)
        self.rect = self.image_surf.get_rect(center=center)
        self.color = BUTTON_COLOR
        self.callback = callback

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        screen.blit(self.image_surf, self.rect)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
            self.color = BUTTON_COLOR
        elif event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos): 
                self.color = BUTTON_HOVER_COLOR
            else:
                self.color = BUTTON_COLOR


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height= self.screen.get_width(), self.screen.get_height()
        self.board = None
        self.ai = None
        self.game_manager = None
        self.state_manager = None

        self.can_press_learn = True

        self.main_menu_buttons = [
            Button('Train Today', self.open_training_view, 
                   (self.screen_width // 2, self.screen_height // 2 - 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Add Opening', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 - 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Practice', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 + 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Settings', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 + 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            IconButton(IMAGE_PATH + 'exit_icon.png', self.exit_application, 
                   (SQUARE_SIZE, self.screen_height - SQUARE_SIZE), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

        self.trainer_buttons = [
            Button('Train', self.train, 
                   (10 * SQUARE_SIZE, 10 * MENU_BUTTON_HEIGHT), (200, MENU_BUTTON_HEIGHT)),
            Button('Learn', self.learn, 
                   (10 * SQUARE_SIZE, 12 * MENU_BUTTON_HEIGHT), (200, MENU_BUTTON_HEIGHT)),
            IconButton(IMAGE_PATH + 'flip_icon.png', self.flip, 
                   (10 * SQUARE_SIZE, 14 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]
    
    def initialize_dependencies(self, board, ai, game_manager, state_manager):
        self.board = board
        self.ai = ai
        self.game_manager = game_manager
        self.state_manager = state_manager

    def handle_event(self, event):
        match self.state_manager.get_state():
            case AppState.MAIN_MENU:
                for button in self.main_menu_buttons:
                    button.handle_event(event)

            case AppState.TRAINING:
                for button in self.trainer_buttons:
                    button.handle_event(event)
        
    def draw(self):
        match self.state_manager.get_state():
            case AppState.QUIT:
                for button in self.main_menu_buttons:
                    button.draw(self.screen)

            case AppState.MAIN_MENU:
                for button in self.main_menu_buttons:
                    button.draw(self.screen)

            case AppState.TRAINING:
                self.board.draw_board()
                for button in self.trainer_buttons:
                    button.draw(self.screen)

    def open_training_view(self):
        self.state_manager.set_state(AppState.TRAINING)
    
    def open_main_menu(self):
        self.state_manager.set_state(AppState.MAIN_MENU)

    def exit_application(self):
        self.state_manager.set_state(AppState.QUIT)

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
