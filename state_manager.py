class AppState:
    QUIT = 0
    MAIN_MENU = 1
    TRAINING = 2
    PRACTICE = 3
    REVIEW = 4
    SETTINGS = 5


class StateManager:
    def __init__(self) -> None:
        self.state = AppState.MAIN_MENU 
    
    def initialize_dependencies(self, board, ai, ui_manager, game_manager): 
        self.board = board
        self.ai = ai
        self.ui_manager = ui_manager
        self.game_manager = game_manager

    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state