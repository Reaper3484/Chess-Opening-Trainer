import pygame
from pygame.locals import *
from config import *
from ui_manager import UIManager
from training import Trainer
from state_manager import StateManager, AppState


class ChessOpeningTrainerApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('Chess Opening Trainer')
        icon = pygame.image.load(IMAGE_PATH + 'app_icon.png')
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode()
        self.clock = pygame.time.Clock()

        self.state_manager = StateManager()
        self.trainer = Trainer(self.screen, self.state_manager)
        self.ui_manager = UIManager(self.screen, self.trainer, self.state_manager)
        self.state_manager.initialize_dependencies(self.ui_manager, self.trainer)
    
    def run(self):
        running = True
        while running:
            if self.state_manager.get_state() == AppState.QUIT:
                running = False
                
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False 

                self.ui_manager.handle_event(event)
                    
            self.screen.fill(SCREEN_BG_COLOR)
            self.ui_manager.update()
            self.ui_manager.draw()

            self.clock.tick(FRAME_RATE)
            pygame.display.update()
        
        pygame.quit()


if __name__ == '__main__':
    app = ChessOpeningTrainerApp()
    app.run()