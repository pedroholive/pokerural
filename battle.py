from settings import *
from sprites import MonsterSprite, MonsterNameSprite, MonsterLevelSprite, MonsterStatsSprite, MonsterOutlineSprite, AttackSprite, TimedSprite
from groups import BattleSprites
from game_data import ATTACK_DATA
from support import draw_bar
from tempo import Tempo
from random import choice

class Battle:
    def __init__(self, player_monsters, opponent_monsters, monster_frames, bg_surf, fonts, end_battle, character, sounds):
        # Inicialização geral da superfície de exibição e assets gráficos/sonoros
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.monster_frames = monster_frames
        self.fonts = fonts
        
        # Dicionário contendo os dados dos monstros do jogador e do oponente
        self.monster_data = {'player': player_monsters, 'opponent': opponent_monsters}
        
        # Flags e referências para controle do estado da batalha e do personagem
        self.battle_over = False
        self.end_battle = end_battle
        self.character = character
        self.sounds = sounds

        # Gerenciamento de temporizadores (ex: delay para o ataque da IA)
        self.timers = {
            'opponent delay': Tempo(600, func = self.opponent_attack)
        }

        # Grupos de sprites para renderização e lógica
        self.battle_sprites   = BattleSprites() # Grupo customizado para ordem de desenho
        self.player_sprites   = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        # Variáveis de controle de seleção e turnos
        self.current_monster = None # Monstro que está agindo no momento
        self.selection_mode  = None # Modo atual do menu (geral, ataques, troca, alvo)
        self.selected_attack = None # Ataque escolhido antes de selecionar o alvo
        self.selection_side  = 'player' # Lado que está sendo selecionado
        
        # Índices para navegação nos menus (listas)
        self.indexes = {
            'general': 0,
            'monster': 0,
            'attacks': 0,
            'switch' : 0,
            'target' : 0,
        }

        # Inicia a configuração dos monstros no campo
        self.setup()

    def setup(self):
        # Itera sobre os dados dos monstros para criar os sprites iniciais
        for entity, monster in self.monster_data.items():
            # Cria apenas os 3 primeiros monstros de cada lado (índice <= 2)
            for index, monster in {k:v for k,v in monster.items() if k <= 2}.items():
                self.create_monster(monster, index, index, entity)

            # Remove os monstros já criados da lista de dados do oponente para evitar duplicação
            for i in range(len(self.opponent_sprites)):
                del self.monster_data['opponent'][i]

    def create_monster(self, monster, index, pos_index, entity):
        # Garante que o monstro não inicie pausado
        monster.paused = False
        
        # Normaliza o nome do monstro para buscar nos assets (minúsculo e sem espaços extras)
        monster_key = monster.name.strip().lower()
        monster_data = self.monster_frames['monsters'][monster_key] 
        
        # Define os frames de animação padrão
        frames = monster_data 
        
        # Verifica se existem frames de contorno (outline), caso contrário usa os normais como fallback
        if 'outlines' in monster_data:
            outline_frames = monster_data['outlines']
        else:
            outline_frames = frames 
            print(f"Aviso: Monstro '{monster_key}' não possui a chave 'outlines'. Usando frames normais.")
            
        # Configuração específica dependendo se é jogador ou oponente
        if entity == 'player':
            # Define posição à esquerda
            pos = list(BATTLE_POSITIONS['left'].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            
            # Espelha as imagens horizontalmente para o monstro do jogador olhar para a direita
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames_list] for state, frames_list in frames.items()}
            outline_frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames_list] for state, frames_list in outline_frames.items()}
        else:
            # Define posição à direita
            pos = list(BATTLE_POSITIONS['right'].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        # Criação do sprite principal do monstro
        monster_sprite = MonsterSprite(pos, frames, groups, monster, index, pos_index, entity, self.apply_attack, self.create_monster)
        
        # Criação do sprite de contorno (seleção)
        MonsterOutlineSprite(monster_sprite, self.battle_sprites, outline_frames)

        # Criação dos elementos de UI vinculados ao monstro (Nome, Nível, Barra de Vida/Energia)
        name_pos = monster_sprite.rect.midleft + vector(16,-70) if entity == 'player' else monster_sprite.rect.midright + vector(-40,-70)
        name_sprite = MonsterNameSprite(name_pos, monster_sprite, self.battle_sprites, self.fonts['regular'])
        level_pos = name_sprite.rect.bottomleft if entity == 'player' else name_sprite.rect.bottomright 
        MonsterLevelSprite(entity, level_pos, monster_sprite, self.battle_sprites, self.fonts['small'])
        MonsterStatsSprite(monster_sprite.rect.midbottom + vector(0,20), monster_sprite, (150,48), self.battle_sprites, self.fonts['small'])
  
    def input(self):
        # Processa entrada apenas se houver um modo de seleção ativo e um monstro agindo
        if self.selection_mode and self.current_monster:
            keys = pygame.key.get_just_pressed()

            # Define o limite de navegação baseado no menu atual
            match self.selection_mode:
                case 'general': limiter = len(BATTLE_CHOICES['full'])
                case 'attacks': limiter = len(self.current_monster.monster.get_abilities(all = False))
                case 'switch': limiter = len(self.available_monsters)
                case 'target': limiter = len(self.opponent_sprites) if self.selection_side == 'opponent' else len(self.player_sprites)

            # Navegação para baixo e para cima nos menus (cíclico)
            if keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] + 1) % limiter
            if keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] - 1) % limiter
            
            # Confirmação da seleção (Barra de Espaço)
            if keys[pygame.K_SPACE]:
                
                # Lógica para trocar de monstro
                if self.selection_mode == 'switch':
                    index, new_monster = list(self.available_monsters.items())[self.indexes['switch']]
                    self.current_monster.kill() # Remove o monstro atual
                    self.create_monster(new_monster, index, self.current_monster.pos_index, 'player') # Cria o novo
                    self.selection_mode = None
                    self.update_all_monsters('resume') # Retoma a batalha

                # Lógica para selecionar um alvo
                if self.selection_mode == 'target':
                    sprite_group = self.opponent_sprites if self.selection_side == 'opponent' else self.player_sprites
                    sprites = {sprite.pos_index: sprite for sprite in sprite_group}
                    monster_sprite = sprites[list(sprites.keys())[self.indexes['target']]]

                    if self.selected_attack:
                        # Executa o ataque selecionado no alvo
                        self.current_monster.activate_attack(monster_sprite, self.selected_attack)
                        self.selected_attack, self.current_monster, self.selection_mode = None, None, None
                    else:
                        # Lógica de captura (se não houver ataque selecionado, assume tentativa de captura)
                        if monster_sprite.monster.health < monster_sprite.monster.get_stat('max_health') * 0.9:
                            # Captura com sucesso se a vida estiver baixa
                            self.monster_data['player'][len(self.monster_data['player'])] = monster_sprite.monster
                            monster_sprite.delayed_kill(None)
                            self.update_all_monsters('resume')
                        else:
                            # Falha na captura
                            TimedSprite(monster_sprite.rect.center, self.monster_frames['ui']['cross'], self.battle_sprites, 1000)

                # Lógica para selecionar um ataque
                if self.selection_mode == 'attacks':
                    self.selection_mode = 'target'
                    self.selected_attack = self.current_monster.monster.get_abilities(all = False)[self.indexes['attacks']]
                    self.selection_side = ATTACK_DATA[self.selected_attack]['target']

                # Lógica do menu geral (Ataque, Defesa, Troca, Captura)
                if self.selection_mode == 'general':
                    if self.indexes['general'] == 0: # Atacar
                        self.selection_mode = 'attacks'
                    
                    if self.indexes['general'] == 1: # Defender
                        self.current_monster.monster.defending = True
                        self.update_all_monsters('resume')
                        self.current_monster, self.selection_mode = None, None
                        self.indexes['general'] = 0
                    
                    if self.indexes['general'] == 2: # Trocar
                        self.selection_mode = 'switch'

                    if self.indexes['general'] == 3: # Capturar
                        self.selection_mode = 'target'
                        self.selection_side = 'opponent'
                
                # Reseta índices após seleção
                self.indexes = {k: 0 for k in self.indexes}

            # Botão de voltar (ESC)
            if keys[pygame.K_ESCAPE]:
                if self.selection_mode in ('attacks', 'switch', 'target'):
                    self.selection_mode = 'general'

    def update_timers(self):
        # Atualiza todos os temporizadores ativos
        for timer in self.timers.values():
            timer.update()

    # Sistema de batalha
    def check_active(self):
        # Verifica a iniciativa de todos os monstros
        for monster_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            if monster_sprite.monster.initiative >= 100:
                # É a vez deste monstro
                monster_sprite.monster.defending = False
                self.update_all_monsters('pause') # Pausa animações dos outros
                monster_sprite.monster.initiative = 0
                monster_sprite.set_highlight(True)
                self.current_monster = monster_sprite
                
                # Se for do jogador, abre o menu; se for oponente, ativa IA
                if self.player_sprites in monster_sprite.groups():
                    self.selection_mode = 'general'
                else:
                    self.timers['opponent delay'].activate()

    def update_all_monsters(self, option):
        # Pausa ou resume todos os monstros em campo
        for monster_sprite in self.player_sprites.sprites() + self.opponent_sprites.sprites():
            monster_sprite.monster.paused = True if option == 'pause' else False

    def apply_attack(self, target_sprite, attack, amount):
        # Cria a animação do ataque e toca o som
        AttackSprite(target_sprite.rect.center, self.monster_frames['attacks'][ATTACK_DATA[attack]['animation']], self.battle_sprites)
        self.sounds[ATTACK_DATA[attack]['animation']].play()

        # Obtém elementos para cálculo de dano
        attack_element = ATTACK_DATA[attack]['element']
        target_element = target_sprite.monster.element

        # Multiplicadores de elemento (Dano Duplo)
        # Fogo > Planta | Água > Fogo | Planta > Água
        if attack_element == 'fire'  and target_element == 'plant' or \
           attack_element == 'water' and target_element == 'fire'  or \
           attack_element == 'plant' and target_element == 'water':
            amount *= 2

        # Multiplicadores de elemento (Dano pela Metade)
        if attack_element == 'fire'  and target_element == 'water' or \
           attack_element == 'water' and target_element == 'plant' or \
           attack_element == 'plant' and target_element == 'fire':
            amount *= 0.5

        # Cálculo de defesa
        target_defense = 1 - target_sprite.monster.get_stat('defense') / 2000
        if target_sprite.monster.defending:
            target_defense -= 0.2 # Bônus de defesa se estiver defendendo
        target_defense = max(0, min(1, target_defense))

        # Aplica o dano à vida do alvo
        target_sprite.monster.health -= amount * target_defense
        self.check_death()

        # Retoma o fluxo da batalha
        self.update_all_monsters('resume')

    def check_death(self):
        # Verifica se algum monstro morreu
        for monster_sprite in self.opponent_sprites.sprites() + self.player_sprites.sprites():
            if monster_sprite.monster.health <= 0:
                if self.player_sprites in monster_sprite.groups(): # Lógica para monstro do jogador
                    active_monsters = [(monster_sprite.index, monster_sprite.monster) for monster_sprite in self.player_sprites.sprites()]
                    # Busca monstros disponíveis no banco
                    available_monsters = [(index, monster) for index, monster in self.monster_data['player'].items() if monster.health > 0 and (index, monster) not in active_monsters]
                    if available_monsters:
                        # Prepara dados para substituição automática
                        new_monster_data = [(monster, index, monster_sprite.pos_index, 'player') for index, monster in available_monsters][0]
                    else:
                        new_monster_data = None
                else: # Lógica para monstro do oponente
                    # Prepara o próximo monstro da lista do oponente
                    new_monster_data = (list(self.monster_data['opponent'].values())[0], monster_sprite.index, monster_sprite.pos_index, 'opponent') if self.monster_data['opponent'] else None
                    if self.monster_data['opponent']:
                        del self.monster_data['opponent'][min(self.monster_data['opponent'])]
                    
                    # Cálculo de XP para os monstros do jogador
                    xp_amount = monster_sprite.monster.level * 100 / len(self.player_sprites)
                    for player_sprite in self.player_sprites:
                        player_sprite.monster.update_xp(xp_amount)

                # Inicia a sequência de morte (animação/remoção) e substituição
                monster_sprite.delayed_kill(new_monster_data)

    def opponent_attack(self):
        # IA simples do oponente: escolhe habilidade e alvo aleatórios
        ability = choice(self.current_monster.monster.get_abilities())
        random_target = choice(self.opponent_sprites.sprites()) if ATTACK_DATA[ability]['target'] == 'player' else choice(self.player_sprites.sprites())
        self.current_monster.activate_attack(random_target, ability)

    def check_end_battle(self):
        # Vitória: Todos os oponentes derrotados
        if len(self.opponent_sprites) == 0 and not self.battle_over:
            self.battle_over = True
            self.end_battle(self.character)
            for monster in self. monster_data['player'].values():
                monster.initiative = 0 # Reseta iniciativa para o futuro

        # Derrota: Todos os monstros do jogador derrotados
        if len(self.player_sprites) == 0:
            pygame.quit()
            exit()


    # Interface de Usuário (UI)
    def draw_ui(self):
        # Desenha o menu apropriado baseado no modo de seleção
        if self.current_monster:
            if self.selection_mode == 'general':
                self.draw_general()
            if self.selection_mode == 'attacks':
                self.draw_attacks()
            if self.selection_mode == 'switch':
                self.draw_switch()

    def draw_general(self):
        # Desenha os ícones do menu principal (Ataque, Defesa, etc.)
        for index, (option, data_dict) in enumerate(BATTLE_CHOICES['full'].items()):
            if index == self.indexes['general']:
                # Ícone iluminado se selecionado
                surf = self.monster_frames['ui'][f"{data_dict['icon']}_highlight"]
            else:
                # Ícone em escala de cinza se não selecionado
                surf = pygame.transform.grayscale(self.monster_frames['ui'][data_dict['icon']])
            rect = surf.get_frect(center = self.current_monster.rect.midright + data_dict['pos'])
            self.display_surface.blit(surf, rect)

    def draw_attacks(self):
        # Dados das habilidades do monstro atual
        abilities = self.current_monster.monster.get_abilities(all = False)
        width, height = 150, 200
        visible_attacks = 4
        item_height = height / visible_attacks
        
        # Cálculo do offset vertical para rolagem da lista (scrolling)
        v_offset = 0 if self.indexes['attacks'] < visible_attacks else -(self.indexes['attacks'] - visible_attacks + 1) * item_height

        # Fundo do menu
        bg_rect = pygame.FRect((0,0), (width,height)).move_to(midleft = self.current_monster.rect.midright + vector(20,0))
        pygame.draw.rect(self.display_surface, COLORS['white'], bg_rect, 0, 5)

        for index, ability in enumerate(abilities):
            selected = index == self.indexes['attacks']

            # Renderização do texto (cor baseada no elemento se selecionado)
            if selected:
                element = ATTACK_DATA[ability]['element']
                text_color = COLORS[element] if element!= 'normal' else COLORS['black']
            else:
                text_color = COLORS['light']
            text_surf  = self.fonts['regular'].render(ability, False, text_color)

            # Retângulos para posicionamento e fundo do item
            text_rect = text_surf.get_frect(center = bg_rect.midtop + vector(0, item_height / 2 + index * item_height + v_offset))
            text_bg_rect = pygame.FRect((0,0), (width, item_height)).move_to(center = text_rect.center)

            # Desenha o item apenas se estiver dentro da área visível do menu (clipping manual)
            if bg_rect.collidepoint(text_rect.center):
                if selected:
                    # Desenha fundo destacado com bordas arredondadas dependendo da posição (topo, meio, fim)
                    if text_bg_rect.collidepoint(bg_rect.topleft):
                        pygame.draw.rect(self.display_surface, COLORS['dark white'], text_bg_rect,0,0,5,5)
                    elif text_bg_rect.collidepoint(bg_rect.midbottom + vector(0,-1)):
                        pygame.draw.rect(self.display_surface, COLORS['dark white'], text_bg_rect,0,0,0,0,5,5)
                    else:
                        pygame.draw.rect(self.display_surface, COLORS['dark white'], text_bg_rect)

                self.display_surface.blit(text_surf, text_rect)

    def draw_switch(self):
        # Configurações visuais do menu de troca
        width, height = 300, 320
        visible_monsters = 4
        item_height = height / visible_monsters
        v_offset = 0 if self.indexes['switch'] < visible_monsters else -(self.indexes['switch'] - visible_monsters + 1) * item_height
        bg_rect = pygame.FRect((0,0), (width, height)).move_to(midleft = self.current_monster.rect.midright + vector(20,0))
        pygame.draw.rect(self.display_surface, COLORS['white'], bg_rect, 0, 5)

        # Filtra monstros disponíveis para troca (vivos e não ativos)
        active_monsters = [(monster_sprite.index, monster_sprite.monster) for monster_sprite in self.player_sprites]
        self.available_monsters = {index: monster for index, monster in self.monster_data['player'].items() if (index, monster) not in active_monsters and monster.health > 0}

        for index, monster in enumerate(self.available_monsters.values()):
            selected = index == self.indexes['switch']
            item_bg_rect = pygame.FRect((0,0), (width, item_height)).move_to(midleft = (bg_rect.left, bg_rect.top + item_height / 2 + index * item_height + v_offset))

            # Desenha ícone e nome do monstro
            icon_surf = self.monster_frames['icons'][monster.name]
            icon_rect = icon_surf.get_frect(midleft = bg_rect.topleft + vector(10,item_height / 2 + index * item_height + v_offset))
            text_surf = self.fonts['regular'].render(f'{monster.name} ({monster.level})', False, COLORS['red'] if selected else COLORS['black'])
            text_rect = text_surf.get_frect(topleft = (bg_rect.left + 90, icon_rect.top))

            # Fundo de seleção
            if selected:
                if item_bg_rect.collidepoint(bg_rect.topleft):
                    pygame.draw.rect(self.display_surface, COLORS['dark white'], item_bg_rect, 0, 0, 5, 5)
                elif item_bg_rect.collidepoint(bg_rect.midbottom + vector(0,-1)):
                    pygame.draw.rect(self.display_surface, COLORS['dark white'], item_bg_rect, 0, 0, 0, 0, 5, 5)
                else:
                    pygame.draw.rect(self.display_surface, COLORS['dark white'], item_bg_rect)

            # Verifica se o item está visível para desenhar
            if bg_rect.collidepoint(item_bg_rect.center):
                for surf, rect in ((icon_surf, icon_rect), (text_surf, text_rect)):
                    self.display_surface.blit(surf, rect)
                # Barras de Vida e Energia no menu de troca
                health_rect = pygame.FRect((text_rect.bottomleft + vector(0,4)), (100,4))
                energy_rect = pygame.FRect((health_rect.bottomleft + vector(0,2)), (80,4))
                draw_bar(self.display_surface, health_rect, monster.health, monster.get_stat('max_health'), COLORS['red'], COLORS['black'])
                draw_bar(self.display_surface, energy_rect, monster.energy, monster.get_stat('max_energy'), COLORS['blue'], COLORS['black'])

    def update(self, dt):
        # Verifica condições de fim de jogo
        self.check_end_battle()
        
        # Atualizações lógicas
        self.input()
        self.update_timers()
        self.battle_sprites.update(dt) # Atualiza animações dos sprites
        self.check_active() # Gerencia turnos

        # Renderização (Desenho)
        self.display_surface.blit(self.bg_surf, (0,0))
        # Desenha sprites passando informações de estado para destaques corretos
        self.battle_sprites.draw(self.current_monster, self.selection_side, self.selection_mode, self.indexes['target'], self.player_sprites, self.opponent_sprites)
        self.draw_ui()