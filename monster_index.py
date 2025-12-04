from settings import * 
from support import draw_bar
from game_data import MONSTER_DATA, ATTACK_DATA

class MonsterIndex:
    """
    Gerencia a Interface de Usuário (UI) para visualizar a equipe de monstros.
    Exibe uma lista rolável à esquerda e detalhes completos à direita.
    Permite trocar a ordem dos monstros.
    """
    def __init__(self, monsters, fonts, monster_frames):
        self.display_surface = pygame.display.get_surface()
        self.fonts = fonts
        self.monsters = monsters # Dicionário com a equipe atual do jogador
        self.frame_index = 0 # Para animar o sprite do monstro na tela de detalhes

        # Recursos gráficos (Dicionários carregados no main.py)
        self.icon_frames = monster_frames['monsters']
        self.monster_frames = monster_frames['monsters']
        self.ui_frames = monster_frames['ui'] # Ícones de ataque, defesa, etc.

        # Superfície escura para o fundo (efeito de "dimming" sobre o jogo)
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_surf.set_alpha(200) # Transparência (0-255)

        # Dimensões da Janela Principal do Menu
        # Cria um retângulo que ocupa 60% da largura e 80% da altura da tela, centralizado
        self.main_rect = pygame.FRect(0, 0, WINDOW_WIDTH * 0.6, WINDOW_HEIGHT * 0.8).move_to(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Configurações da Lista Lateral (Esquerda)
        self.visible_items = 6 # Quantos monstros aparecem de uma vez sem rolar
        self.list_width = self.main_rect.width * 0.3 # A lista ocupa 30% da largura do menu
        self.item_height = self.main_rect.height / self.visible_items # Altura de cada botão
        self.index = 0 # Qual monstro está destacado atualmente
        self.selected_index = None # Qual monstro foi selecionado para troca (Swap)

        # Cálculo dos Valores Máximos (Normalização de Stats)
        # Necessário para desenhar as barras de atributos proporcionalmente (0 a 100%)
        self.max_stats = {}
        for data in MONSTER_DATA.values():
            for stat, value in data['stats'].items():
                if stat != 'element':
                    # Encontra o maior valor base existente no jogo para cada atributo
                    if stat not in self.max_stats:
                        self.max_stats[stat] = value
                    else:
                        self.max_stats[stat] = value if value > self.max_stats[stat] else self.max_stats[stat]
        
        # Ajusta chaves para bater com os atributos da classe Monster
        self.max_stats['health'] = self.max_stats.pop('max_health')
        self.max_stats['energy'] = self.max_stats.pop('max_energy')

    def input(self):
        """
        Controla a navegação e a lógica de troca (swap) de monstros.
        """
        keys = pygame.key.get_just_pressed()
        
        # Navegação Vertical
        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1
        
        # Ação de Seleção/Troca
        if keys[pygame.K_SPACE]:
            if self.selected_index != None:
                # SE JÁ TEM UM SELECIONADO: Realiza a troca de posição
                selected_monster = self.monsters[self.selected_index]
                current_monster  = self.monsters[self.index]
                
                # Troca os valores no dicionário
                self.monsters[self.index] = selected_monster
                self.monsters[self.selected_index] = current_monster
                
                # Limpa a seleção
                self.selected_index = None
            else:
                # SE NÃO TEM NINGUÉM SELECIONADO: Marca o atual para troca
                self.selected_index = self.index

        # Garante que o índice sempre esteja dentro dos limites da lista (loop infinito)
        self.index = self.index % len(self.monsters)

    def display_list(self):
        """
        Renderiza a barra lateral esquerda com a lista de monstros.
        """
        # Desenha o fundo da lista (Cinza escuro) com cantos arredondados na esquerda
        bg_rect = pygame.FRect(self.main_rect.topleft, (self.list_width, self.main_rect.height))
        pygame.draw.rect(self.display_surface, COLORS['gray'], bg_rect, 0, 0, 12, 0, 12, 0)

        # Cálculo de Rolagem (Scroll)
        # Se o índice for maior que o número de itens visíveis, sobe a lista
        v_offset = 0 if self.index < self.visible_items else -(self.index - self.visible_items + 1) * self.item_height
        
        for index, monster in self.monsters.items():
            # Define as cores: Destaque se o cursor estiver em cima, Dourado se estiver selecionado para troca
            bg_color = COLORS['gray'] if self.index != index else COLORS['light']
            text_color = COLORS['white'] if self.selected_index != index else COLORS['gold']

            # Calcula a posição vertical do item considerando o scroll
            top = self.main_rect.top + index * self.item_height + v_offset
            item_rect = pygame.FRect(self.main_rect.left, top, self.list_width, self.item_height)
            
            # Renderiza Nome e Retângulo de Texto
            text_surf = self.fonts['regular'].render(monster.name, False, text_color)
            text_rect = text_surf.get_frect(midleft = item_rect.midleft + vector(90, 0))

            # Recupera o ícone do monstro (Navegando na estrutura do dicionário de assets)
            frames_dict = self.icon_frames[monster.name] 
            frames_list = list(frames_dict.values())[0] # Pega a lista de animações
            icon_surf = frames_list[0] # Pega o primeiro frame (estático)
            icon_rect = icon_surf.get_frect(center = item_rect.midleft + vector(45,0))

            # Lógica de Clipping (Só desenha se estiver dentro da área principal)
            if item_rect.colliderect(self.main_rect):
                # Arredonda cantos específicos se for o primeiro ou último item visível
                if item_rect.collidepoint(self.main_rect.topleft):
                    pygame.draw.rect(self.display_surface, bg_color, item_rect, 0, 0, 12) # Canto superior esquerdo arredondado
                elif item_rect.collidepoint(self.main_rect.bottomleft + vector(1,-1)):
                    pygame.draw.rect(self.display_surface, bg_color, item_rect, 0, 0, 0, 0, 12, 0) # Canto inferior esquerdo arredondado
                else:
                    pygame.draw.rect(self.display_surface, bg_color, item_rect) # Quadrado normal
                
                # Desenha texto e ícone
                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(icon_surf, icon_rect)

        # Desenha linhas separadoras entre os itens
        for i in range(1, min(self.visible_items, len(self.monsters))):
            y = self.main_rect.top + self.item_height * i
            left = self.main_rect.left
            right = self.main_rect.left + self.list_width
            pygame.draw.line(self.display_surface, COLORS['light-gray'], (left, y), (right, y))

        # Desenha uma sombra vertical para separar a lista da área de detalhes
        shadow_surf = pygame.Surface((4, self.main_rect.height))
        shadow_surf.set_alpha(100)
        self.display_surface.blit(shadow_surf, (self.main_rect.left + self.list_width - 4, self.main_rect.top))
    
    def display_main(self, dt):
        """
        Renderiza a área principal (direita) com os detalhes do monstro.
        """
        # Pega os dados do monstro atualmente destacado
        monster = self.monsters[self.index]

        # Fundo da área principal (Escuro com cantos arredondados na direita)
        rect = pygame.FRect(self.main_rect.left + self.list_width, self.main_rect.top, self.main_rect.width - self.list_width, self.main_rect.height)
        pygame.draw.rect(self.display_surface, COLORS['dark'], rect, 0, 12, 0, 12, 0)

        # --- CABEÇALHO (Topo) ---
        # Retângulo colorido baseado no elemento do monstro
        top_rect = pygame.FRect(rect.topleft, (rect.width, rect.height * 0.4))
        pygame.draw.rect(self.display_surface, COLORS[monster.element], top_rect, 0, 0, 0, 12)

        # Animação do Sprite Grande
        self.frame_index += ANIMATION_SPEED * dt
        monster_surf = self.monster_frames[monster.name]['idle'][int(self.frame_index) % len(self.monster_frames[monster.name]['idle'])]
        monster_rect = monster_surf.get_frect(center = top_rect.center)
        self.display_surface.blit(monster_surf, monster_rect)

        # Informações Básicas (Nome, Nível, Elemento)
        name_surf = self.fonts['bold'].render(monster.name, False, COLORS['white'])
        name_rect = name_surf.get_frect(topleft = top_rect.topleft + vector(10,10))
        self.display_surface.blit(name_surf, name_rect)

        # Barra de XP (logo abaixo do nível)
        level_surf = self.fonts['regular'].render(f'Lvl: {monster.level}', False, COLORS['white'])
        level_rect = level_surf.get_frect(bottomleft = top_rect.bottomleft + vector(10,-16))
        self.display_surface.blit(level_surf, level_rect)
        
        draw_bar(
            surface = self.display_surface, 
            rect = pygame.FRect(level_rect.bottomleft, (100,4)), 
            value = monster.xp, 
            max_value = monster.level_up, 
            color = COLORS['white'], 
            bg_color = COLORS['dark'])

        element_surf = self.fonts['regular'].render(monster.element, False, COLORS['white'])
        element_rect = element_surf.get_frect(bottomright = top_rect.bottomright + vector(-10,-10))
        self.display_surface.blit(element_surf, element_rect)

        # --- BARRAS DE STATUS (HP e Energia) ---
        bar_data = {
            'width': rect.width * 0.45,
            'height': 30,
            'top': top_rect.bottom + rect.width * 0.03,
            'left_side': rect.left + rect.width / 4,
            'right_side': rect.left + rect.width * 3/4
        }

        # Barra de HP (Vermelha)
        healthbar_rect = pygame.FRect((0,0), (bar_data['width'], bar_data['height'])).move_to(midtop = (bar_data['left_side'], bar_data['top']))
        draw_bar(self.display_surface, healthbar_rect, monster.health, monster.get_stat('max_health'), COLORS['red'], COLORS['black'], 2)
        hp_text = self.fonts['regular'].render(f"HP: {int(monster.health)}/{int(monster.get_stat('max_health'))}", False, COLORS['white'])
        hp_rect = hp_text.get_frect(midleft = healthbar_rect.midleft + vector(10,0))
        self.display_surface.blit(hp_text, hp_rect)

        # Barra de Energia/EP (Azul)
        energybar_rect = pygame.FRect((0,0), (bar_data['width'], bar_data['height'])).move_to(midtop = (bar_data['right_side'], bar_data['top']))
        draw_bar(self.display_surface, energybar_rect, monster.energy, monster.get_stat('max_energy'), COLORS['blue'], COLORS['black'], 2)
        ep_text = self.fonts['regular'].render(f"EP: {int(monster.energy)}/{int(monster.get_stat('max_energy'))}", False, COLORS['white'])
        ep_rect = ep_text.get_frect(midleft = energybar_rect.midleft + vector(10,0))
        self.display_surface.blit(ep_text, ep_rect)

        # --- SEÇÃO INFERIOR: Atributos e Habilidades ---
        sides = {'left': healthbar_rect.left, 'right': energybar_rect.left}
        info_height = rect.bottom - healthbar_rect.bottom

        # 1. Atributos (Attack, Defense, Speed, etc.) - Coluna Esquerda
        stats_rect = pygame.FRect(sides['left'], healthbar_rect.bottom, healthbar_rect.width, info_height).inflate(0,-60).move(0,15)
        stats_text_surf = self.fonts['regular'].render('Stats', False, COLORS['white'])
        stats_text_rect = stats_text_surf.get_frect(bottomleft = stats_rect.topleft)
        self.display_surface.blit(stats_text_surf, stats_text_rect)

        monster_stats = monster.get_stats()
        stat_height = stats_rect.height / len(monster_stats)

        for index, (stat, value) in enumerate(monster_stats.items()):
            single_stat_rect = pygame.FRect(stats_rect.left, stats_rect.top + index * stat_height, stats_rect.width, stat_height)

            # Ícone do Atributo
            icon_surf = self.ui_frames[stat]
            icon_rect = icon_surf.get_frect(midleft = single_stat_rect.midleft + vector(5,0))
            self.display_surface.blit(icon_surf, icon_rect)

            # Nome do Atributo
            text_surf = self.fonts['regular'].render(stat, False, COLORS['white'])
            text_rect = text_surf.get_frect(topleft = icon_rect.topleft + vector(30,-10))
            self.display_surface.blit(text_surf, text_rect)

            # Barra de Progresso do Atributo (Branca)
            # Calcula o tamanho baseado no 'max_stats' global para mostrar quão forte o monstro é comparado ao máximo possível
            bar_rect = pygame.FRect((text_rect.left, text_rect.bottom + 2), (single_stat_rect.width - (text_rect.left - single_stat_rect.left), 4))
            draw_bar(self.display_surface, bar_rect, value, self.max_stats[stat] * monster.level, COLORS['white'], COLORS['black'])

        # 2. Habilidades (Abilities) - Coluna Direita
        ability_rect = stats_rect.copy().move_to(left = sides['right'])
        ability_text_surf = self.fonts['regular'].render('Ability', False, COLORS['white'])
        ability_text_rect = ability_text_surf.get_frect(bottomleft = ability_rect.topleft)
        self.display_surface.blit(ability_text_surf, ability_text_rect)

        # Lista as habilidades em formato de Grid (2 colunas)
        for index, ability in enumerate(monster.get_abilities()):
            element = ATTACK_DATA[ability]['element'] # Pega o elemento do ataque para colorir

            text_surf = self.fonts['regular'].render(ability, False, COLORS['black'])
            
            # Lógica de posicionamento em Grid
            x = ability_rect.left + index % 2 * ability_rect.width / 2 # Coluna 0 ou 1
            y = 20 + ability_rect.top + int(index / 2) * (text_surf.get_height() + 20) # Linha 0, 1, 2...
            
            rect = text_surf.get_frect(topleft = (x,y))
            
            # Fundo colorido do botão da habilidade
            pygame.draw.rect(self.display_surface, COLORS[element], rect.inflate(10,10), 0, 4)
            self.display_surface.blit(text_surf, rect)

    def update(self, dt):
        """
        Loop principal do menu.
        """
        self.input() # Checa teclas
        self.display_surface.blit(self.tint_surf, (0,0)) # Desenha fundo escuro
        self.display_list() # Desenha lista
        self.display_main(dt) # Desenha detalhes