from settings import * 
from support import import_image
from entities import Entity

class AllSprites(pygame.sprite.Group):
    """
    Grupo de sprites personalizado para o MUNDO ABERTO (Overworld).
    Funciona como uma CÂMERA que segue o jogador e gerencia a profundidade (Y-Sort).
    """
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector() # Vetor que armazena o deslocamento da câmera
        
        # Importa gráficos auxiliares (sombra para os personagens e ícone de alerta)
        self.shadow_surf = import_image('graphics', 'other', 'shadow')
        self.notice_surf = import_image('graphics', 'ui', 'notice')

    def draw(self, player):
        """
        Desenha todos os sprites levando em conta a posição do jogador.
        """
        
        # --- CÁLCULO DA CÂMERA ---
        # A lógica é: Queremos que o player fique no centro da tela.
        # Para isso, movemos o mundo na direção oposta ao movimento do player.
        # Fórmula: -(posição_player - metade_da_tela)
        self.offset.x = -(player.rect.centerx - WINDOW_WIDTH / 2)
        self.offset.y = -(player.rect.centery - WINDOW_HEIGHT / 2)

        # --- SEPARAÇÃO POR CAMADAS (LAYERS) ---
        # Filtra os sprites em 3 listas baseadas no Z-Index definido em settings.py
        
        # 1. Background (Chão): Desenhado primeiro (fica atrás de tudo)
        bg_sprites = [sprite for sprite in self if sprite.z < WORLD_LAYERS['main']]
        
        # 2. Main (Personagens/Objetos): Desenhado no meio.
        # IMPORTANTE: Ordenado pelo 'y_sort' (base do sprite). 
        # Quem tem o Y maior (está mais embaixo na tela) é desenhado por último, ficando "na frente".
        # Isso cria o efeito de profundidade 2.5D.
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key = lambda sprite: sprite.y_sort)
        
        # 3. Foreground (Topo de árvores): Desenhado por último (fica na frente de tudo)
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        # --- LOOP DE DESENHO ---
        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer:
                # Se for uma entidade (Player/NPC), desenha a sombra antes do corpo
                if isinstance(sprite, Entity):
                    # Desenha a sombra deslocada um pouco para baixo e direita (40, 110)
                    self.display_surface.blit(self.shadow_surf, sprite.rect.topleft + self.offset + vector(40,110))
                
                # Desenha o sprite na posição correta aplicando o offset da câmera
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                
                # Se este sprite for o jogador e ele tiver sido notado por um inimigo
                if sprite == player and player.noticed:
                    # Desenha o ícone de exclamação (!) acima da cabeça dele
                    rect = self.notice_surf.get_frect(midbottom = sprite.rect.midtop)
                    self.display_surface.blit(self.notice_surf, rect.topleft + self.offset)

class BattleSprites(pygame.sprite.Group):
    """
    Grupo de sprites personalizado para a BATALHA.
    Gerencia o desenho dos monstros, fundos e UI de seleção (contornos brancos).
    """
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def draw(self, current_monster_sprite, side, mode, target_index, player_sprites, opponent_sprites):
        """
        Desenha a cena de batalha e destaca quem está atacando ou sendo atacado.
        """
        
        # --- LÓGICA DE ALVO ---
        # Determina qual grupo de sprites (jogador ou oponente) está sendo mirado
        sprite_group = opponent_sprites if side == 'opponent' else player_sprites
        # Cria um dicionário para acessar os sprites pela posição (pos_index)
        sprites = {sprite.pos_index: sprite for sprite in sprite_group}
        
        # Identifica o sprite específico que está sendo alvejado no momento
        monster_sprite = sprites[list(sprites.keys())[target_index]] if sprites else None

        # --- LOOP DE DESENHO (Ordenado por Z) ---
        for sprite in sorted(self, key = lambda sprite: sprite.z):
            
            # Se o sprite for um "Outline" (o contorno branco de seleção)
            if sprite.z == BATTLE_LAYERS['outline']:
                
                # Lógica complexa para decidir se deve desenhar o contorno ou não:
                # 1. Desenha se for o monstro ATUAL agindo (para saber quem é a vez)
                #    ...mas não desenha se estiver escolhendo um alvo no próprio time (cura).
                # OU
                # 2. Desenha se for o monstro ALVO (monster_sprite) e estamos no modo de escolha de alvo ('target').
                if sprite.monster_sprite == current_monster_sprite and not (mode == 'target' and side == 'player') or\
                   sprite.monster_sprite == monster_sprite and sprite.monster_sprite.entity == side and mode and mode == 'target':
                    self.display_surface.blit(sprite.image, sprite.rect)
            
            # Se for qualquer outro sprite (chão, monstro, UI), desenha normalmente
            else:
                self.display_surface.blit(sprite.image, sprite.rect)