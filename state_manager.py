class AppState:
    QUIT = 0
    MAIN_MENU = 1
    TRAINING = 2
    ADD_OPENING = 3
    PRACTICE = 4
    REVIEW = 5
    SETTINGS = 6


class StateManager:
    def __init__(self) -> None:
        self.state = AppState.MAIN_MENU 
        self.is_training_opening = False

    def initialize_dependencies(self, board, ui_manager, game_manager, trainer): 
        self.board = board
        self.ui_manager = ui_manager
        self.game_manager = game_manager
        self.trainer = trainer

    def get_user_response(self):
        for button in self.ui_manager.review_buttons:
            button.set_active(True)

    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state