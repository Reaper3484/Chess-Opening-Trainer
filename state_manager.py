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
                    move_number = self.ui_manager.trainer.board.move_number
                    if move_number % 2:
                        self.ui_manager.trainer_moves_display.add_item([move_notation])
                    else:
                        self.ui_manager.trainer_moves_display.items[move_number // 2 - 1].append(move_notation) 
                    self.trainer.train()

            case AppState.ADD_OPENING:
                move_number = self.ui_manager.opening_adder_board.move_number
                if move_number % 2:
                    self.ui_manager.moves_display.add_item([move_notation])
                else:
                    self.ui_manager.moves_display.items[move_number // 2 - 1].append(move_notation) 

    def add_trainer_move(self, move_notation):
        move_number = self.ui_manager.trainer.board.move_number
        if move_number % 2:
            self.ui_manager.trainer_moves_display.add_item([move_notation])
        else:
            self.ui_manager.trainer_moves_display.items[move_number // 2 - 1].append(move_notation) 
    
    def board_undo(self):
        match self.state:
            case AppState.TRAINING:
                self.ui_manager.trainer_moves_display.delete_last_item()
            case AppState.ADD_OPENING:
                self.ui_manager.moves_display.delete_last_item()

    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state