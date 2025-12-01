from settings import *
import pygame
from pytmx.util_pygame import load_pygame
from os.path import join
from sprite import Sprite
from entities import Player

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        #groups
        self.all_sprites = pygame.sprite.Group()
        
        self.import_assets()
        # CORREÇÃO 1: Acessar 'world' via self.tmx_maps e remover 'self' extra na chamada
        self.setup(self.tmx_maps['world'], 'house') 
        
    def import_assets(self):
        # Define self.tmx_maps para ser acessível em self.setup()
        self.tmx_maps = {'world': load_pygame(join('..','Pokerural', 'data', 'maps', 'world.tmx'))}
        
    # CORREÇÃO 3: Assumindo que a definição do setup está correta (self, tmx_map, player_start_pos)
    
    def setup(self, tmx_map, player_start_pos):
        for x, y, surf in tmx_map.get_layer_by_name('Terrain').tiles():
        # Verificação CRÍTICA
            if surf and isinstance(surf, pygame.Surface):
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
            else:
            # Imprima uma mensagem se um tile falhar
                print(f"ERRO: Tile em ({x}, {y}) não é uma Surface válida.") 
            # Se você vir esta mensagem, o problema está no carregamento do PyTMX/tileset.
            
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player' and obj.properties['pos'] == player_start_pos:
                Player((obj.x, obj.y), self.all_sprites)
            
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    
            self.display_surface.fill('black')        
            self.all_sprites.draw(self.display_surface) 
            pygame.display.update()
        
if __name__ == "__main__":
    game = Game()
    game.run()