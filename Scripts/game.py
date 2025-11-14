import pygame
from settings import CORES
from player import Player

class Game: 
    def __init__(self, tela):
        self.tela = tela
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(x=100, y=100, imagens_path = '')
        
    def run(self):
        while self.running:
            self.eventos_jogo()
            self.atualiza()

    def eventos_jogo(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def atualiza(self):
        pass
    
    def draw(self):
        self.tela.fill(CORES['black'])
        pygame.display.flip()