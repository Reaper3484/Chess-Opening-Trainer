import pygame
from  pygame.locals import *
from constants import *
from state_manager import AppState
import pygame


class DisplayText:
    def __init__(self, text, position, font_name=FONT, font_size=FONT_SIZE, text_color=(0, 0, 0), bg_color=None, bold=False, italic=False):
        self.text = text
        self.position = position
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.bold = bold
        self.italic = italic
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.bold, self.italic)
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)

    def draw(self, screen):
        screen.blit(self.rendered_text, self.text_rect)

    def set_text(self, new_text):
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)

    def set_position(self, new_position):
        self.position = new_position
        self.text_rect.center = self.position

    def set_font(self, font_name, font_size, bold=False, italic=False):
        self.font_name = font_name
        self.font_size = font_size
        self.bold = bold
        self.italic = italic
        self.font = pygame.font.SysFont(self.font_name, self.font_size, self.bold, self.italic)
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)

    def set_color(self, text_color, bg_color=None):
        self.text_color = text_color
        self.bg_color = bg_color
        self.rendered_text = self.font.render(self.text, True, self.text_color, self.bg_color)
        self.text_rect = self.rendered_text.get_rect(center=self.position)


class Button:
    def __init__(self, text, callback, center, size, 
                 idle_color=BUTTON_IDLE_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                 pressed_color=BUTTON_PRESSED_COLOR, inactive_color=BUTTON_INACTIVE_COLOR, 
                 shadow_color=BUTTON_SHADOW_COLOR, font=FONT, font_size=FONT_SIZE, 
                 font_color=FONT_COLOR, padding=BUTTON_PADDING, is_active=True):

        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.button_rect = self.rect.move(-padding, -padding)
        self.text = text
        self.callback = callback

        self.idle_color = idle_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.inactive_color = inactive_color
        self.active_shadow_color = shadow_color

        self.font = pygame.font.Font(font, font_size)
        self.font_color = font_color

        if is_active:
            self.color = idle_color
            self.shadow_color = shadow_color
        else:
            self.color = inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR

        self.hover = False
        self.active = is_active
        self.pressed = False
        self.padding = padding

    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect(center=self.button_rect.center)

        if self.pressed:
            text_rect = text_rect.move(self.padding, self.padding)
            pygame.draw.rect(screen, self.color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        else:
            pygame.draw.rect(screen, self.shadow_color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
            pygame.draw.rect(screen, self.color, self.button_rect, border_radius=BUTTON_BORDER_RADIUS)
        
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if not self.active:
            self.color = BUTTON_INACTIVE_COLOR
            self.shadow_color = BUTTON_SHADOW_COLOR
            return
        else:
            self.shadow_color = self.active_shadow_color

        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
            self.color = self.pressed_color

        elif event.type == MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                self.color = self.idle_color
                if self.rect.collidepoint(event.pos):
                    self.callback()

        elif event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.color = self.hover_color
            else:
                self.color = self.idle_color

    def set_active(self, active):
        self.active = active
        if not self.active:
            self.color = self.inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR
        else:
            self.color = self.idle_color
            self.shadow_color = self.active_shadow_color


class IconButton:
    def __init__(self, image_path, callback, center, size, 
                 idle_color=BUTTON_IDLE_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                 pressed_color=BUTTON_PRESSED_COLOR, inactive_color=BUTTON_INACTIVE_COLOR, 
                 shadow_color=BUTTON_SHADOW_COLOR, padding=BUTTON_PADDING, is_active=True):

        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center
        self.button_rect = self.rect.move(-padding, -padding)
        image = pygame.image.load(image_path).convert_alpha()
        self.image_surf = pygame.transform.scale(image, size)
        self.callback = callback

        self.idle_color = idle_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.inactive_color = inactive_color
        self.active_shadow_color = shadow_color

        if is_active:
            self.color = idle_color
            self.shadow_color = shadow_color
        else:
            self.color = inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR

        self.hover = False
        self.active = is_active
        self.pressed = False
        self.padding = padding

    def draw(self, screen):
        image_rect = self.image_surf.get_rect(center=self.button_rect.center)

        if self.pressed:
            image_rect = image_rect.move(self.padding, self.padding)
            pygame.draw.rect(screen, self.color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        else:
            pygame.draw.rect(screen, self.shadow_color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
            pygame.draw.rect(screen, self.color, self.button_rect, border_radius=BUTTON_BORDER_RADIUS)
        
        screen.blit(self.image_surf, image_rect)

    def handle_event(self, event):
        if not self.active:
            self.color = BUTTON_INACTIVE_COLOR
            self.shadow_color = BUTTON_SHADOW_COLOR
            return
        else:
            self.shadow_color = self.active_shadow_color

        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
            self.color = self.pressed_color

        elif event.type == MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                self.color = self.idle_color
                if self.rect.collidepoint(event.pos):
                    self.callback()

        elif event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.color = self.hover_color
            else:
                self.color = self.idle_color

    def set_active(self, active):
        self.active = active
        if not self.active:
            self.color = self.inactive_color
            self.shadow_color = BUTTON_SHADOW_COLOR
        else:
            self.color = self.idle_color
            self.shadow_color = self.active_shadow_color


class UIManager:
    def __init__(self, screen, trainer, opening_adder, practice_manager, state_manager):
        self.screen = screen
        self.trainer = trainer
        self.opening_adder = opening_adder
        self.practice_manager = practice_manager
        self.state_manager = state_manager
        self.screen_width, self.screen_height= self.screen.get_width(), self.screen.get_height()
        self.initialize()

    def initialize(self):
        self.main_menu_buttons = [
            Button('Train Today', self.open_training_view, 
                   (self.screen_width // 2, self.screen_height // 2 - 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Add Opening', self.open_add_opening_view, 
                   (self.screen_width // 2, self.screen_height // 2 - 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Practice', self.open_practice_view, 
                   (self.screen_width // 2, self.screen_height // 2 + 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Settings', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 + 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            IconButton(IMAGE_PATH + 'exit_icon.png', self.exit_application, 
                   (SQUARE_SIZE, self.screen_height - SQUARE_SIZE), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

        self.trainer_buttons = [
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
            IconButton(IMAGE_PATH + 'flip_icon.png', self.flip, 
                   (self.screen_width - 2 * SQUARE_SIZE, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

        self.review_buttons = [
            Button('Again', self.set_response_again, 
                   (2 * SQUARE_SIZE, 9 * SQUARE_SIZE), (170, 80), AGAIN_IDLE_COLOR, AGAIN_HOVER_COLOR, AGAIN_PRESSED_COLOR, BUTTON_INACTIVE_COLOR, AGAIN_SHADOW_COLOR, is_active=False),
            Button('Hard', self.set_response_hard, 
                   (4 * SQUARE_SIZE, 9 * SQUARE_SIZE), (170, 80), HARD_IDLE_COLOR, HARD_HOVER_COLOR, HARD_PRESSED_COLOR, BUTTON_INACTIVE_COLOR, HARD_SHADOW_COLOR, is_active=False),
            Button('Good', self.set_response_good, 
                   (6 * SQUARE_SIZE, 9 * SQUARE_SIZE), (170, 80), GOOD_IDLE_COLOR, GOOD_HOVER_COLOR, GOOD_PRESSED_COLOR, BUTTON_INACTIVE_COLOR, GOOD_SHADOW_COLOR, is_active=False),
        ]

        self.trainer_main_text = DisplayText(None, (4 * SQUARE_SIZE, 8 * SQUARE_SIZE + 40), font_size=70, text_color='black', bg_color=BUTTON_IDLE_COLOR)

        self.add_opening_buttons = [
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

        self.practice_buttons = [
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

    def handle_event(self, event):
        match self.state_manager.get_state():
            case AppState.MAIN_MENU:
                for button in self.main_menu_buttons:
                    button.handle_event(event)

            case AppState.TRAINING:
                self.trainer.board.handle_event(event)
                for button in self.trainer_buttons:
                    button.handle_event(event)
                for button in self.review_buttons:
                    button.handle_event(event)

            case AppState.ADD_OPENING:
                self.opening_adder.board.handle_event(event)
                for button in self.add_opening_buttons:
                    button.handle_event(event)

            case AppState.PRACTICE:
                self.practice_manager.board.handle_event(event)
                for button in self.practice_buttons:
                    button.handle_event(event)
                
    def draw(self):
        match self.state_manager.get_state():
            case AppState.MAIN_MENU:
                for button in self.main_menu_buttons:
                    button.draw(self.screen)

            case AppState.TRAINING:
                self.trainer.board.draw_board()
                for button in self.trainer_buttons:
                    button.draw(self.screen)
                for button in self.review_buttons:
                    button.draw(self.screen)

                self.trainer_main_text.draw(self.screen)
            
            case AppState.ADD_OPENING:
                self.opening_adder.board.draw_board()
                for button in self.add_opening_buttons:
                    button.draw(self.screen)

            case AppState.PRACTICE:
                self.practice_manager.board.draw_board()
                for button in self.practice_buttons:
                    button.draw(self.screen)

            case _:
                for button in self.main_menu_buttons:
                    button.draw(self.screen)

    def update(self):
        match self.state_manager.get_state():
            case AppState.QUIT:
                pass

            case AppState.MAIN_MENU:
                pass

            case AppState.TRAINING:
                pass

    def open_main_menu(self):
        self.state_manager.set_state(AppState.MAIN_MENU)

    def open_training_view(self):
        self.state_manager.set_state(AppState.TRAINING)
        if self.trainer.is_training_batch_finished:
            self.train()

    def open_add_opening_view(self):
        self.state_manager.set_state(AppState.ADD_OPENING)

    def open_practice_view(self):
        self.state_manager.set_state(AppState.PRACTICE)

    def exit_application(self):
        self.state_manager.set_state(AppState.QUIT)
    
    def train(self):
        opening_name = self.trainer.train_next()
        self.trainer_main_text.set_text(opening_name)

    def set_response_good(self):
        self.trainer.submit_user_response('Good')
        self.train()
        for button in self.review_buttons:
            button.set_active(False)
        
    def set_response_hard(self):
        self.trainer.submit_user_response('Hard')
        self.train()
        for button in self.review_buttons:
            button.set_active(False)

    def set_response_again(self):
        self.trainer.submit_user_response('Again')
        self.train()
        for button in self.review_buttons:
            button.set_active(False)

    def flip(self):
        match self.state_manager.get_state():
            case AppState.TRAINING:
                self.trainer.board.flip()
            case AppState.ADD_OPENING:
                self.opening_adder.board.flip()
            