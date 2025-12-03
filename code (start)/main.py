from settings import *
import pygame
from pytmx.util_pygame import load_pygame
from os.path import join
from sprite import Sprite, AnimatedSprite, MonsterPatchSprite
from entities import Player, Character
from groups import AllSprites
from support import * 
class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('PokeRural')
        self.clock = pygame.time.Clock()
        
        #groups
        self.all_sprites = AllSprites()
        self.player = None
        self.import_assets()
        # CORREÇÃO 1: Acessar 'world' via self.tmx_maps e remover 'self' extra na chamada
        self.setup(self.tmx_maps['world'], 'house') 
        
    def import_assets(self):
        # Define self.tmx_maps para ser acessível em self.setup()
        self.tmx_maps = {
            'world': load_pygame(join('..','Pokerural', 'data', 'maps', 'world.tmx')),
            'hospital': load_pygame(join('..','Pokerural', 'data', 'maps', 'hospital.tmx'))
            }
        
        self.overworld_frames = {
            'water': import_folder('..','Pokerural', 'graphics', 'tilesets', 'water'),
            'cost' : coast_importer(24, 12, '..', 'Pokerural', 'graphics', 'tilesets', 'coast'),
            'characters': all_character_import('..', 'Pokerural', 'graphics', 'characters')
        
        }
        
    # CORREÇÃO 3: Assumindo que a definição do setup está correta (self, tmx_map, player_start_pos)
    
    def setup(self, tmx_map, player_start_pos):
        size = 'default'
        
        #terreno 
        for layer in ['Terrain', 'Terrain Top']:
            map_layer = tmx_map.get_layer_by_name(layer)
            if map_layer: # Verifica se a camada foi encontrada
                for x, y, surf in map_layer.tiles():
                    if surf: 
                        Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites), z = WORLD_LAYERS['bg'])
        
        #water
        for obj in tmx_map.get_layer_by_name('Water'): 
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                   AnimatedSprite((obj.x, obj.y), self.overworld_frames['water'], self.all_sprites, z=WORLD_LAYERS['water'])
        
        #coast
        for obj in tmx_map.get_layer_by_name('Coast'):
            terrain = obj.properties['terrain']
            side = obj.properties['side']  
            AnimatedSprite((obj.x, obj.y), self.overworld_frames['cost'][terrain][side], self.all_sprites, z = WORLD_LAYERS['bg'])
                
        #objetos do mapa
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'top':
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, WORLD_LAYERS['top'])
            else:
                Sprite((obj.x, obj.y), obj.image, self.all_sprites)
        
        #grass patches
        for obj in tmx_map.get_layer_by_name('Monsters'):
            MonsterPatchSprite((obj.x, obj.y), obj.image, self.all_sprites, obj.properties['biome'])
            
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                if obj.properties['pos'] == player_start_pos: 
                    self.player = Player(
                        pos = (obj.x, obj.y), 
                        frames = self.overworld_frames['characters']['player'], groups = self.all_sprites,
                        facing_direction = obj.properties['direction'])
            elif 'graphic' in obj.properties:
                Character(
                    pos=(obj.x, obj.y),
                    frames=self.overworld_frames['characters'][obj.properties['graphic']],
                    groups=self.all_sprites,
                    facing_direction = obj.properties['direction']
                    )

            else:
                print(f"[AVISO] Objeto ignorado em Entities: {obj.name}")
        
        
                           
    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    
            self.all_sprites.update(dt)        
            self.display_surface.fill('black')        
             
            if self.player: 
                self.all_sprites.draw(self.player.rect.center)
            else:
                # Este else é útil para depuração, mostrando que o setup falhou.
                print("ERRO DE SETUP: O objeto 'Player' não foi encontrado no mapa.") 
            pygame.display.update()
        
if __name__ == "__main__":
    game = Game()
    game.run()