import pygame

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, imagens_path):
        """"Inicializa o jogador
        x: Posição inicial no eixo x
        y: Posição inicial no eixo y
        imagem_path: Caminho para a imagem"""
        super().__init__()
        self.x = x
        self.y = y
        self.speed = 3
        
        self.frame_width = 48
        self.frame_height = 48
        
        self.frame = pygame.image.load(imagens_path).convert_alpha()