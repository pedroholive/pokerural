from settings import * 
from game_data import *
from pytmx.util_pygame import load_pygame
from os.path import join
from random import randint

# Importações das classes personalizadas do jogo
from sprites import Sprite, AnimatedSprite, MonsterPatchSprite, BorderSprite, CollidableSprite, TransitionSprite
from entities import Player, Character
from groups import AllSprites
from dialog import DialogTree
from monster_index import MonsterIndex
from battle import Battle
from tempo import Tempo
from evolution import Evolution

from support import *
from monster import Monster


class Game:
    """
    Classe Principal (Game Controller).
    Gerencia o ciclo de vida do jogo, estados (exploração, batalha, menus),
    carregamento de assets e loop principal.
    """
    def __init__(self):
        # 1. Configuração Inicial do Pygame e Janela
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Hunter')
        self.clock = pygame.time.Clock()
        
        # Timer para evitar encontrar monstros a cada milissegundo (cooldown de 2s)
        self.encounter_timer = Tempo(2000, func = self.monster_encounter)

        # 2. Criação da Equipe do Jogador (Dados Persistentes)
        self.player_monsters = {
            0: Monster('embercan', 16),
            1: Monster('capiblu', 15),
            2: Monster('wardensawi', 18),
        }
        # Adiciona um pouco de XP aleatório inicial para variar os status
        for monster in self.player_monsters.values():
            monster.xp += randint(0,monster.level * 100)

        # Monstros de teste (apenas para debug ou placeholders)
        self.test_monsters = {
            0: Monster('jatyglow', 10),
            1: Monster('apexwing', 13),
            2: Monster('araclaw', 12),
        }

        # 3. Grupos de Sprites (Organização Visual e Lógica)
        self.all_sprites = AllSprites() # Câmera e desenho ordenado
        self.collision_sprites = pygame.sprite.Group() # Paredes e obstáculos
        self.character_sprites = pygame.sprite.Group() # NPCs
        self.transition_sprites = pygame.sprite.Group() # Gatilhos de mudança de mapa
        self.monster_sprites = pygame.sprite.Group() # Grama alta (encontros)

        # 4. Sistema de Transição de Tela (Fade in/out)
        self.transition_target = None # Para onde vamos? (Batalha, Mapa ou None)
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)) # Tela preta sobreposta
        self.tint_mode = 'untint' # Estado atual: clareando ou escurecendo
        self.tint_progress = 0 # Opacidade (0 a 255)
        self.tint_direction = -1
        self.tint_speed = 600 # Velocidade do fade

        # Carrega imagens, sons e mapas
        self.import_assets()
        
        self.player = None
        # Carrega o mapa inicial ('world') e define o ponto de spawn ('house')
        self.setup(self.tmx_maps['world'], 'house')
        self.audio['overworld'].play(-1) # Toca música em loop

        # 5. Inicialização de Overlays (Interfaces que pausam o jogo)
        self.dialog_tree = None
        self.monster_index = MonsterIndex(self.player_monsters, self.fonts, self.monster_frames)
        self.index_open = False # Se o menu de monstros está aberto
        self.battle = None
        self.evolution = None


    def import_assets(self):
        """
        Carrega todos os recursos gráficos, áudio e mapas para a memória.
        """
        self.tmx_maps = tmx_importer('data', 'maps')

        # Gráficos do Mundo (Overworld)
        self.overworld_frames = {
            'water': import_folder('graphics', 'tilesets', 'water'),
            'coast': coast_importer(24, 12, 'graphics', 'tilesets', 'coast'),
            'characters': all_character_import('graphics', 'characters')
        }

        # Gráficos dos Monstros e UI
        self.monster_frames = {
            'icons': import_folder_dict('graphics', 'monsters'),
            'monsters': monster_importer(4, 2, 'graphics', 'monsters'),
            'ui': import_folder_dict('graphics', 'ui'),
            'attacks': attack_importer('graphics', 'attacks')
        }

        # --- TRATAMENTO DE ERROS DE NOMES (CRÍTICO) ---
        # Alguns sistemas operacionais diferenciam 'Embercan' de 'embercan'.
        # Este bloco converte todas as chaves de monstros para minúsculas e remove espaços.
        raw_monsters = self.monster_frames['monsters']
        standardized_monsters = {
            name.strip().lower(): frames_data 
            for name, frames_data in raw_monsters.items()
        }
        self.monster_frames['monsters'] = standardized_monsters
        # ---------------------------------------------

        # Cria ícones estáticos para a interface (pega o primeiro frame da animação)
        self.icon_frames = {}
        for name, frames_dict in self.monster_frames['monsters'].items():
            # Pega a lista de animações (geralmente 'idle' ou a primeira disponível)
            frames_list = list(frames_dict.values())[0]
            # O frame 0 é usado como ícone estático no menu
            self.icon_frames[name] = frames_list[0]

        # Fontes e Imagens de Fundo
        self.fonts = {
            'dialog': pygame.font.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 30),
            'regular': pygame.font.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 18),
            'small': pygame.font.Font(join('graphics', 'fonts', 'PixeloidSans.ttf'), 14),
            'bold': pygame.font.Font(join('graphics', 'fonts', 'dogicapixelbold.otf'), 20),
        }
        self.bg_frames = import_folder_dict('graphics', 'backgrounds')
        self.start_animation_frames = import_folder('graphics', 'other', 'star animation')
    
        # Áudio
        self.audio = audio_importer('audio')

    def setup(self, tmx_map, player_start_pos):
        """
        Reconstrói o mapa do jogo baseado no arquivo Tiled (TMX).
        Limpa os sprites antigos e posiciona tiles, colisão e NPCs.
        """
        # Limpa grupos antigos
        for group in (self.all_sprites, self.collision_sprites, self.transition_sprites, self.character_sprites):
            group.empty()

        # Camadas de Terreno (Chão estático)
        for layer in ['Terrain', 'Terrain Top']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, WORLD_LAYERS['bg'])

        # Camada de Água (Animada)
        for obj in tmx_map.get_layer_by_name('Water'):
            # Preenche a área retangular definida no Tiled com tiles de água
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite((x,y), self.overworld_frames['water'], self.all_sprites, WORLD_LAYERS['water'])

        # Camada de Costa/Praia (Lógica complexa para bordas de água)
        for obj in tmx_map.get_layer_by_name('Coast'):
            terrain = obj.properties['terrain']
            side = obj.properties['side']
            AnimatedSprite((obj.x, obj.y), self.overworld_frames['coast'][terrain][side], self.all_sprites, WORLD_LAYERS['bg'])
        
        # Objetos (Árvores, Pedras, Decoração)
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'top':
                # Objetos puramente visuais que ficam acima do chão
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, WORLD_LAYERS['top'])
            else:
                # Objetos que bloqueiam o jogador (Collidable)
                CollidableSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        # Objetos de Transição (Portas e passagens para outros mapas)
        for obj in tmx_map.get_layer_by_name('Transition'):
            TransitionSprite((obj.x, obj.y), (obj.width, obj.height), (obj.properties['target'], obj.properties['pos']), self.transition_sprites)

        # Colisões Invisíveis (Paredes desenhadas no Tiled)
        for obj in tmx_map.get_layer_by_name('Collisions'):
            BorderSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        # Grama Alta (Áreas de encontro de monstros)
        for obj in tmx_map.get_layer_by_name('Monsters'):
            MonsterPatchSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.monster_sprites), obj.properties['biome'], obj.properties['monsters'], obj.properties['level'])

        # Entidades (Player e NPCs)
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                # Cria o jogador apenas se o 'pos' (ex: 'house') bater com o argumento da função
                if obj.properties['pos'] == player_start_pos:
                    self.player = Player(
                        pos = (obj.x, obj.y), 
                        frames = self.overworld_frames['characters']['player'], 
                        groups = self.all_sprites,
                        facing_direction = obj.properties['direction'], 
                        collision_sprites = self.collision_sprites)
            else:
                # Cria NPCs (Treinadores ou Enfermeiras)
                Character(
                    pos = (obj.x, obj.y), 
                    frames = self.overworld_frames['characters'][obj.properties['graphic']], 
                    groups = (self.all_sprites, self.collision_sprites, self.character_sprites),
                    facing_direction = obj.properties['direction'],
                    character_data = TRAINER_DATA[obj.properties['character_id']], # Pega dados do settings.py
                    player = self.player,
                    create_dialog = self.create_dialog,
                    collision_sprites = self.collision_sprites,
                    radius = obj.properties['radius'],
                    nurse = obj.properties['character_id'] == 'Nurse',
                    notice_sound = self.audio['notice'])

    # --- SISTEMA DE DIÁLOGO ---
    def input(self):
        """
        Gerencia inputs globais que não são de movimento (Interagir, Menu).
        """
        # Só aceita input se não houver diálogo ou batalha acontecendo
        if not self.dialog_tree and not self.battle:
            keys = pygame.key.get_just_pressed()
            
            # Tecla ESPAÇO: Interagir com NPCs
            if keys[pygame.K_SPACE]:
                for character in self.character_sprites:
                    # Verifica se o player está olhando para o NPC e próximo o suficiente
                    if check_connections(100, self.player, character):
                        self.player.block() # Trava movimento
                        character.change_facing_direction(self.player.rect.center) # NPC olha pro player
                        self.create_dialog(character)
                        character.can_rotate = False # NPC para de girar

            # Tecla ENTER: Abrir/Fechar Pokédex (Menu de monstros)
            if keys[pygame.K_RETURN]:
                self.index_open = not self.index_open
                self.player.blocked = not self.player.blocked # Trava/Destrava player

    def create_dialog(self, character):
        # Inicia a instância da árvore de diálogos
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(character, self.player, self.all_sprites, self.fonts['dialog'], self.end_dialog)

    def end_dialog(self, character):
        """
        Chamado quando o diálogo termina. Define o que acontece depois.
        """
        self.dialog_tree = None
        
        # Caso 1: Enfermeira -> Cura todos os monstros
        if character.nurse:
            for monster in self.player_monsters.values():
                monster.health = monster.get_stat('max_health')
                monster.energy = monster.get_stat('max_energy')
            self.player.unblock()
        
        # Caso 2: Treinador não derrotado -> Inicia Batalha
        elif not character.character_data['defeated']:
            self.audio['overworld'].stop()
            self.audio['battle'].play(-1)
            
            # Prepara a transição para o modo Batalha
            self.transition_target = Battle(
                player_monsters = self.player_monsters, 
                opponent_monsters = character.monsters, 
                monster_frames = self.monster_frames, 
                bg_surf = self.bg_frames[character.character_data['biome']], 
                fonts = self.fonts, 
                end_battle = self.end_battle,
                character = character, 
                sounds = self.audio)
            self.tint_mode = 'tint' # Escurece a tela para transição
        
        # Caso 3: Treinador já derrotado ou Conversa casual -> Apenas libera o player
        else:
            self.player.unblock()
            self.check_evolution()

    # --- SISTEMA DE TRANSIÇÃO (Mapas e Modos de Jogo) ---
    def transition_check(self):
        # Verifica se o player pisou em um sprite de transição
        sprites = [sprite for sprite in self.transition_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites:
            self.player.block()
            self.transition_target = sprites[0].target
            self.tint_mode = 'tint' # Começa a escurecer a tela

    def tint_screen(self, dt):
        """
        Gerencia o efeito visual de Fade In / Fade Out.
        """
        if self.tint_mode == 'untint':
            self.tint_progress -= self.tint_speed * dt # Clareia

        if self.tint_mode == 'tint':
            self.tint_progress += self.tint_speed * dt # Escurece
            
            # Quando a tela está totalmente preta (255)
            if self.tint_progress >= 255:
                # Troca o estado do jogo
                if type(self.transition_target) == Battle:
                    self.battle = self.transition_target # Inicia Batalha
                elif self.transition_target == 'level':
                    self.battle = None # Sai da Batalha
                else:
                    # Muda de Mapa (setup novo)
                    self.setup(self.tmx_maps[self.transition_target[0]], self.transition_target[1])
                
                # Inverte o fade para clarear novamente
                self.tint_mode = 'untint'
                self.transition_target = None

        # Garante que o valor fique entre 0 e 255 e aplica na superfície preta
        self.tint_progress = max(0, min(self.tint_progress, 255))
        self.tint_surf.set_alpha(self.tint_progress)
        self.display_surface.blit(self.tint_surf, (0,0))
    
    def end_battle(self, character):
        """
        Chamado de dentro da classe Battle quando a luta acaba.
        """
        self.audio['battle'].stop()
        self.transition_target = 'level' # Código para voltar ao mapa
        self.tint_mode = 'tint'
        
        if character:
            character.character_data['defeated'] = True # Marca NPC como vencido
            self.create_dialog(character) # Mostra diálogo de derrota
        elif not self.evolution:
            self.player.unblock()
            self.check_evolution()

    def check_evolution(self):
        """
        Verifica se algum monstro do player atingiu o nível de evolução.
        """
        for index, monster in self.player_monsters.items():
            if monster.evolution:
                if monster.level == monster.evolution[1]:
                    self.audio['evolution'].play()
                    self.player.block()
                    # Inicia o Overlay de Evolução
                    self.evolution = Evolution(self.monster_frames['monsters'], monster.name, monster.evolution[0], self.fonts['bold'], self.end_evolution, self.start_animation_frames)
                    # Substitui o monstro antigo pelo novo
                    self.player_monsters[index] = Monster(monster.evolution[0], monster.level)
        
        # Se não houver evolução, volta a música do mapa
        if not self.evolution:
            self.audio['overworld'].play(-1)

    def end_evolution(self):
        self.evolution = None
        self.player.unblock()
        self.audio['evolution'].stop()
        self.audio['overworld'].play(-1)

    # --- SISTEMA DE ENCONTROS ALEATÓRIOS ---
    def check_monster(self):
        # Se player pisar na grama alta, não estiver em batalha e estiver se movendo
        if [sprite for sprite in self.monster_sprites if sprite.rect.colliderect(self.player.hitbox)] and not self.battle and self.player.direction:
            if not self.encounter_timer.active:
                self.encounter_timer.activate()

    def monster_encounter(self):
        """
        Gera uma batalha contra monstro selvagem.
        """
        sprites = [sprite for sprite in self.monster_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites and self.player.direction:
            # Reseta timer com valor aleatório para o próximo encontro
            self.encounter_timer.duration = randint(800, 2500)
            self.player.block()
            self.audio['overworld'].stop()
            self.audio['battle'].play(-1)
            
            # Cria batalha com monstros definidos no bioma da grama
            self.transition_target = Battle(
                player_monsters = self.player_monsters, 
                opponent_monsters = {index:Monster(monster, sprites[0].level + randint(-3,3)) for index, monster in enumerate(sprites[0].monsters)}, 
                monster_frames = self.monster_frames, 
                bg_surf = self.bg_frames[sprites[0].biome], 
                fonts = self.fonts, 
                end_battle = self.end_battle,
                character = None, # None = Selvagem
                sounds = self.audio)
            self.tint_mode = 'tint'

    def run(self):
        """
        Loop principal do Jogo (Game Loop).
        1. Calcula Delta Time.
        2. Processa Eventos.
        3. Atualiza Lógica.
        4. Desenha na Tela.
        """
        while True:
            dt = self.clock.tick() / 1000
            self.display_surface.fill('black')

            # Loop de Eventos (Pygame)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Updates de Lógica
            self.encounter_timer.update()
            self.input()
            self.transition_check()
            self.all_sprites.update(dt) # Move personagens, anima água, etc.
            self.check_monster()
            
            # Desenho (Render)
            self.all_sprites.draw(self.player) # Desenha o mundo com câmera focada no player
            
            # Desenho de Overlays (Camadas superiores)
            # A ordem importa: o que desenha por último fica em cima.
            if self.dialog_tree: self.dialog_tree.update()
            if self.index_open:  self.monster_index.update(dt)
            if self.battle:      self.battle.update(dt)
            if self.evolution:   self.evolution.update(dt)

            # Desenha o efeito de escurecer tela por último de tudo
            self.tint_screen(dt)
            pygame.display.update()

if __name__ == '__main__':
    # Inicializa a classe e começa o jogo
    game = Game()
    game.run()