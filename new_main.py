import pygame
from pygame.locals import *
from constants import *
from board import Board 
from ui import UIManager
from chess_logic import GameManager
from training import AI
from event_handler import EventHandler

class ChessOpeningTrainerApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('Chess Opening Trainer')
        self.screen = pygame.display.set_mode()
        self.clock = pygame.time.Clock()
        self.board = Board(self.screen)
        self.ui_manager = UIManager(self.screen)
        self.game_manager = GameManager()
        self.ai = AI()
        self.event_handler = EventHandler()
        self.set_dependencies()
    
    def run(self):
        self.board.import_fen('rnbqkbnr/pppppppp/////PPPPPPPP/RNBQKBNR w KQkq -')
        self.board.moves_list.append(self.board.generate_fen())
        self.game_manager.update_legal_moves()

        running = True
        while running:
            for event in pygame.event.get():
                self.event_handler.handle_event(event)
                    
            self.screen.fill(SCREEN_BG_COLOR)
            self.board.draw_board()
            self.ui_manager.draw()
            self.clock.tick(FRAME_RATE)
            pygame.display.update()
        
        pygame.quit()
    
    def set_dependencies(self):
        self.board.initialize_dependencies(self.game_manager, self.ui_manager)
        self.ui_manager.initialize_dependencies(self.board, self.ai, self.game_manager)
        self.game_manager.initialize_dependencies(self.board)
        self.ai.initialize_dependencies(self.board, self.game_manager)
        self.event_handler.initialize_dependencies(self.board, self.ui_manager, self.ai, self.game_manager)

if __name__ == '__main__':
    app = ChessOpeningTrainerApp()
    app.run()