import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT 
from game import Game

def main():
    pygame.init()
    
    tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PokeRural")
    
    game = Game(tela) # Passa a tela para a classe Game
    
    game.run()
    
    pygame.quit()
    
if __name__ == '__main__':
    main()