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

    def initialize_dependencies(self, ui_manager, trainer): 
        self.ui_manager = ui_manager
        self.trainer = trainer

    def get_user_response(self):
        for button in self.ui_manager.review_buttons:
            button.set_active(True)

    def move_made(self, move_notation):
        match self.state:
            case AppState.TRAINING:
                if not self.trainer.is_training_batch_finished:
                    self.trainer.train()
                # self.ui_manager.moves_display.add_item(move_notation)

            case AppState.ADD_OPENING:
                self.ui_manager.moves_display.add_item(move_notation)

    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state