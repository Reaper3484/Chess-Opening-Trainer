import pyperclip
from  pygame.locals import *
from constants import *
from state_manager import AppState
from board import Board
from ui_elements import *


class UIManager:
    def __init__(self, screen, trainer, state_manager):
        self.screen = screen
        self.trainer = trainer
        self.state_manager = state_manager
        self.opening_adder_board = Board(self.screen, self.state_manager)
        self.practice_board = Board(self.screen, self.state_manager)
        self.screen_width, self.screen_height= self.screen.get_width(), self.screen.get_height()
        self.initialize()

    def initialize(self):
        self.main_menu_elements = [
            Button('Train Today', self.open_training_view, 
                   (self.screen_width // 2, self.screen_height // 2 - 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Opening Manager', self.open_opening_manager_view, 
                   (self.screen_width // 2, self.screen_height // 2 - 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Practice', self.open_practice_view, 
                   (self.screen_width // 2, self.screen_height // 2 + 1 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            Button('Settings', self.train, 
                   (self.screen_width // 2, self.screen_height // 2 + 3 * MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            IconButton(IMAGE_PATH + 'exit_icon.png', self.exit_application, 
                   (SQUARE_SIZE, self.screen_height - SQUARE_SIZE), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

        self.trainer_main_text = Text(None, (4 * SQUARE_SIZE, 8 * SQUARE_SIZE + 40), font_size=70, text_color='black', bg_color=BUTTON_IDLE_COLOR)
        self.trainer_moves_display = ScrollableList((8 * SQUARE_SIZE + 30, MENU_BUTTON_HEIGHT * 3 - 10), (TEXT_BOX_WIDTH, SQUARE_SIZE * 4), 2)

        self.trainer_elements = [
            self.trainer_main_text,
            self.trainer_moves_display,
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE // 2, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

        self.review_buttons = [
            Button('Again', self.set_response_again, 
                   (2 * SQUARE_SIZE, 9 * SQUARE_SIZE), (170, 80), AGAIN_IDLE_COLOR, AGAIN_HOVER_COLOR, AGAIN_PRESSED_COLOR, BUTTON_INACTIVE_COLOR, AGAIN_SHADOW_COLOR, is_active=False),
            Button('Hard', self.set_response_hard, 
                   (4 * SQUARE_SIZE, 9 * SQUARE_SIZE), (170, 80), HARD_IDLE_COLOR, HARD_HOVER_COLOR, HARD_PRESSED_COLOR, BUTTON_INACTIVE_COLOR, HARD_SHADOW_COLOR, is_active=False),
            Button('Good', self.set_response_good, 
                   (6 * SQUARE_SIZE, 9 * SQUARE_SIZE), (170, 80), GOOD_IDLE_COLOR, GOOD_HOVER_COLOR, GOOD_PRESSED_COLOR, BUTTON_INACTIVE_COLOR, GOOD_SHADOW_COLOR, is_active=False),
        ]

        self.openings_list = ClickableList((20, MENU_BUTTON_HEIGHT), (MENU_BUTTON_LENGTH, 10 * MENU_BUTTON_HEIGHT), 1, self.display_opening_info)
        [self.openings_list.add_item([item['name']]) for item in self.trainer.opening_data['openings']]
        self.opening_manager_elements = [
            self.openings_list,
            Button('Add opening', self.open_add_opening_view, (20 + MENU_BUTTON_LENGTH // 2, 12 * MENU_BUTTON_HEIGHT), 
                   (MENU_BUTTON_LENGTH, MENU_BUTTON_HEIGHT)),
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE // 2, MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40))
        ]

        self.fen_text_box = TextBox((11 * SQUARE_SIZE + 20, MENU_BUTTON_HEIGHT * 2 + 10), TEXT_BOX_WIDTH, MENU_BUTTON_HEIGHT, self.validate_fen)
        self.valid_fen_icon = Icon(None, (14 * SQUARE_SIZE - 60, MENU_BUTTON_HEIGHT * 2 - 20), (MENU_BUTTON_HEIGHT - 30, MENU_BUTTON_HEIGHT - 30))
        self.moves_display = ScrollableList((8 * SQUARE_SIZE + 30, MENU_BUTTON_HEIGHT * 3 - 10), (TEXT_BOX_WIDTH, SQUARE_SIZE * 4), 2)
        self.new_opening_name = TextBox((11 * SQUARE_SIZE + 20, MENU_BUTTON_HEIGHT), TEXT_BOX_WIDTH, MENU_BUTTON_HEIGHT)
        self.add_opening_button = Button('Add', self.add_opening, (9 * SQUARE_SIZE, 7 * SQUARE_SIZE), (170, 80), is_active=False)
        self.opening_adder_flip = IconButton(IMAGE_PATH + 'flip_icon.png', self.flip, 
                                             (self.screen_width - SQUARE_SIZE // 2, MENU_BUTTON_HEIGHT * 3 + 20), 
                                             (SQUARE_SIZE - 40, SQUARE_SIZE - 40))

        self.opening_adder_elements = [
            self.fen_text_box,
            self.valid_fen_icon,
            self.moves_display,
            self.new_opening_name,
            self.add_opening_button,
            self.opening_adder_flip,
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_opening_manager_view, 
                   (self.screen_width - SQUARE_SIZE // 2, MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
            IconButton(IMAGE_PATH + 'paste_icon.png', self.paste_fen, 
                   (self.screen_width - SQUARE_SIZE // 2, MENU_BUTTON_HEIGHT * 2 + 10), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
            Button('Cancel', self.reset_opening_view, (11 * SQUARE_SIZE, 7 * SQUARE_SIZE), (220, 80))
        ]

        self.practice_elements = [
            IconButton(IMAGE_PATH + 'back_icon.png', self.open_main_menu, 
                   (self.screen_width - SQUARE_SIZE // 2, 1 * MENU_BUTTON_HEIGHT), (SQUARE_SIZE - 40, SQUARE_SIZE - 40)),
        ]

    def handle_event(self, event):
        match self.state_manager.get_state():
            case AppState.MAIN_MENU:
                for element in self.main_menu_elements:
                    element.handle_event(event)

            case AppState.TRAINING:
                self.trainer.board.handle_event(event)
                for element in self.trainer_elements:
                    element.handle_event(event)
                for button in self.review_buttons:
                    button.handle_event(event)

            case AppState.ADD_OPENING:
                self.opening_adder_board.handle_event(event)
                if self.new_opening_name.text and self.opening_adder_board.move_number > 1:
                    self.add_opening_button.set_active(True)
                else:
                    self.add_opening_button.set_active(False)

                if self.opening_adder_board.move_number:
                    self.opening_adder_flip.set_active(False)
                else: 
                    self.opening_adder_flip.set_active(True)

                for element in self.opening_adder_elements:
                    element.handle_event(event)

            case AppState.OPENING_MANAGER:
                for element in self.opening_manager_elements:
                    element.handle_event(event)

            case AppState.PRACTICE:
                self.practice_board.handle_event(event)
                for element in self.practice_elements:
                    element.handle_event(event)
                
    def draw(self):
        match self.state_manager.get_state():
            case AppState.MAIN_MENU:
                for element in self.main_menu_elements:
                    element.draw(self.screen)

            case AppState.TRAINING:
                self.trainer.board.draw_board()
                for element in self.trainer_elements:
                    element.draw(self.screen)
                for button in self.review_buttons:
                    button.draw(self.screen)

            case AppState.ADD_OPENING:
                self.opening_adder_board.draw_board()
                for element in self.opening_adder_elements:
                    element.draw(self.screen)

            case AppState.PRACTICE:
                self.practice_board.draw_board()
                for element in self.practice_elements:
                    element.draw(self.screen)

            case AppState.OPENING_MANAGER:
                for element in self.opening_manager_elements:
                    element.draw(self.screen)
    
            case _:
                for element in self.main_menu_elements:
                    element.draw(self.screen)

    def update(self):
        match self.state_manager.get_state():
            case AppState.QUIT:
                pass

            case AppState.MAIN_MENU:
                pass

            case AppState.TRAINING:
                pass

            case AppState.OPENING_MANAGER:
                for element in self.opening_manager_elements:
                    element.update()

            case AppState.ADD_OPENING:
                for element in self.opening_adder_elements:
                    element.update()

    def open_main_menu(self):
        self.state_manager.set_state(AppState.MAIN_MENU)

    def open_training_view(self):
        self.state_manager.set_state(AppState.TRAINING)
        if self.trainer.is_training_batch_finished:
            self.train()

    def open_opening_manager_view(self):
        self.state_manager.set_state(AppState.OPENING_MANAGER)

    def open_add_opening_view(self):
        self.state_manager.set_state(AppState.ADD_OPENING)

    def open_practice_view(self):
        self.state_manager.set_state(AppState.PRACTICE)

    def exit_application(self):
        self.state_manager.set_state(AppState.QUIT)

    def train(self):
        self.trainer_moves_display.clear_items()
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
                self.trainer.board.reset()
            case AppState.ADD_OPENING:
                new_colour = 'b' if self.opening_adder_board.user_colour == 'w' else 'w'
                self.opening_adder_board.reset_board(new_colour)

    def paste_fen(self):
        text = pyperclip.paste()
        self.fen_text_box.set_text(text)
        self.validate_fen(text)

    def validate_fen(self, fen):
        old_fen = self.opening_adder.board.generate_fen()
        try:
            self.opening_adder.board.import_fen(fen)
            self.valid_fen_icon.set_icon(IMAGE_PATH + 'green_check_icon.png')
        except:
            self.opening_adder.board.import_fen(old_fen)
            self.valid_fen_icon.set_icon(IMAGE_PATH + 'red_cross_icon.png')

    def add_opening(self):
        name = self.new_opening_name.text
        moves = self.opening_adder_board.moves_list
        user_colour = self.opening_adder_board.user_colour
        notations_list = self.opening_adder_board.notations_list
        self.trainer.add_new_opening(name, user_colour, moves, notations_list) 
        self.reset_opening_view()
        self.train()
        self.openings_list.add_item([name])

    def reset_opening_view(self):
        self.new_opening_name.set_text('')
        self.opening_adder_board.reset_board('w')
        self.opening_adder_flip.set_active(True)
        self.moves_display.clear_items()

    def display_opening_info(self):
        pass