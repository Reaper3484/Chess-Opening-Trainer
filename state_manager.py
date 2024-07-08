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

    def initialize_dependencies(self, ui_manager, trainer, opening_adder, practice_manager): 
        self.ui_manager = ui_manager
        self.trainer = trainer
        self.opening_adder = opening_adder
        self.practice_manager = practice_manager

    def get_user_response(self):
        for button in self.ui_manager.review_buttons:
            button.set_active(True)

    def move_made(self):
        match self.state:
            case AppState.TRAINING:
                self.trainer.train()
            case _:
                return True

    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state