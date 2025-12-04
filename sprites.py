from settings import * 
from random import uniform
from support import draw_bar
from tempo import Tempo

# ==============================================================================
# SPRITES DO MUNDO (OVERWORLD)
# ==============================================================================

class Sprite(pygame.sprite.Sprite):
    """
    Classe base para objetos estáticos do mundo (árvores, chão, pedras).
    """
    def __init__(self, pos, surf, groups, z = WORLD_LAYERS['main']):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(topleft = pos) # Posição flutuante para precisão
        self.z = z # Camada de desenho (Z-Index)
        
        # Y-Sort: Define a linha base para profundidade.
        # Objetos com Y maior são desenhados DEPOIS (ficam na frente).
        self.y_sort = self.rect.centery 
        self.hitbox = self.rect.copy() # Cópia do retângulo para cálculos de colisão

class BorderSprite(Sprite):
    """
    Colisões invisíveis (paredes do mapa). Herda de Sprite mas não precisa de lógica extra.
    """
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy()

class TransitionSprite(Sprite):
    """
    Gatilhos invisíveis de mudança de mapa.
    """
    def __init__(self, pos, size, target, groups):
        surf = pygame.Surface(size) # Cria uma superfície vazia do tamanho do gatilho
        super().__init__(pos, surf, groups)
        self.target = target # Guarda o destino (nome do mapa e posição de spawn)

class CollidableSprite(Sprite):
    """
    Objetos visíveis que bloqueiam o jogador (ex: pedras, tocos).
    """
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        # Reduz a hitbox verticalmente em 60% para permitir que o jogador 
        # ande "atrás" do topo do objeto, criando efeito 2.5D.
        self.hitbox = self.rect.inflate(0, -self.rect.height * 0.6)

class MonsterPatchSprite(Sprite):
    """
    Grama alta onde batalhas aleatórias ocorrem.
    """
    def __init__(self, pos, surf, groups, biome, monsters, level):
        self.biome = biome
        # Define a camada. Se for areia, fica no fundo (bg), senão no principal.
        super().__init__(pos, surf, groups, WORLD_LAYERS['main' if biome != 'sand' else 'bg'])
        
        # Ajusta o Y-Sort para -40. Isso faz a grama ser desenhada "atrás" 
        # do jogador quando ele pisa nela, dando a ilusão que ele está dentro da grama.
        self.y_sort -= 40
        self.biome = biome
        self.monsters = monsters.split(',') # Converte string 'rato,cobra' em lista ['rato', 'cobra']
        self.level = level

class AnimatedSprite(Sprite):
    """
    Sprites do mundo que possuem animação (água, flores, costa).
    """
    def __init__(self, pos, frames, groups, z = WORLD_LAYERS['main']):
        self.frame_index, self.frames = 0, frames
        # Inicia com o primeiro quadro da animação
        super().__init__(pos, frames[self.frame_index], groups, z)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        # Loop infinito da animação usando resto da divisão (%)
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)

# ==============================================================================
# SPRITES DE BATALHA
# ==============================================================================

class MonsterSprite(pygame.sprite.Sprite):
    """
    O sprite principal do monstro na batalha.
    Controla animação, flash de dano e comunicação com a lógica de combate.
    """
    def __init__(self, pos, frames, groups, monster, index, pos_index, entity, apply_attack, create_monster):
        # Dados de Identificação
        self.index = index # Índice na equipe (0, 1, 2)
        self.pos_index = pos_index # Posição na tela ('top', 'center', 'bottom')
        self.entity = entity # 'player' ou 'opponent'
        self.monster = monster # Referência ao objeto de dados (Lógica)
        
        # Configuração de Animação
        self.frame_index, self.frames, self.state = 0, frames, 'idle'
        # Adiciona variação aleatória na velocidade para monstros iguais não sincronizarem
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)
        self.z = BATTLE_LAYERS['monster']
        
        # Efeitos e Lógica de Ataque
        self.highlight = False # Controla o flash branco
        self.target_sprite = None # Quem eu vou atacar?
        self.current_attack = None # Qual ataque vou usar?
        self.apply_attack = apply_attack # Função callback para causar dano real
        self.create_monster = create_monster # Função callback para invocar o próximo monstro se este morrer

        # Setup Pygame
        super().__init__(groups)
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center = pos)

        # Timers Especiais
        self.timers = {
            'remove highlight': Tempo(300, func = lambda: self.set_highlight(False)), # Duração do flash branco
            'kill': Tempo(600, func = self.destroy) # Tempo da animação de morte antes de sumir
        }

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        
        # LÓGICA DE EVENTO DE ANIMAÇÃO:
        # Se estiver atacando e a animação acabou, aplica o dano e volta a ficar parado.
        if self.state == 'attack' and self.frame_index >= len(self.frames['attack']):
            self.apply_attack(self.target_sprite, self.current_attack, self.monster.get_base_damage(self.current_attack))
            self.state = 'idle'

        # Loop da animação seguro
        self.adjusted_frame_index = int(self.frame_index % len(self.frames[self.state]))
        self.image = self.frames[self.state][self.adjusted_frame_index]

        # Efeito de Flash Branco (Hit/Seleção)
        if self.highlight:
            # Cria uma máscara (silhueta) e converte em superfície branca
            white_surf = pygame.mask.from_surface(self.image).to_surface()
            white_surf.set_colorkey('black') # Remove o fundo preto da máscara
            self.image = white_surf # Substitui a imagem colorida pela branca temporariamente

    def set_highlight(self, value):
        self.highlight = value
        if value: 
            self.timers['remove highlight'].activate()

    def activate_attack(self, target_sprite, attack):
        """ Inicia a sequência de ataque visual. """
        self.state = 'attack'
        self.frame_index = 0
        self.target_sprite = target_sprite
        self.current_attack = attack
        self.monster.reduce_energy(attack) # Gasta energia imediatamente

    def delayed_kill(self, new_monster):
        """ Inicia o timer de morte. new_monster é quem vai substituir este (se houver). """
        if not self.timers['kill'].active:
            self.next_monster_data = new_monster
            self.timers['kill'].activate()

    def destroy(self):
        """ Remove o sprite e chama a criação do substituto. """
        if self.next_monster_data:
            self.create_monster(*self.next_monster_data)
        self.kill() # Remove do grupo de sprites (some da tela)

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()
        self.animate(dt)
        self.monster.update(dt) # Atualiza a lógica do monstro (iniciativa, etc)

class MonsterOutlineSprite(pygame.sprite.Sprite):
    """
    Desenha o contorno branco atrás do monstro (usado para seleção).
    Segue exatamente a animação do MonsterSprite pai.
    """
    def __init__(self, monster_sprite, groups, frames):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['outline']
        self.monster_sprite = monster_sprite
        self.frames = frames

        self.image = self.frames[self.monster_sprite.state][self.monster_sprite.frame_index]
        self.rect = self.image.get_frect(center = self.monster_sprite.rect.center)

    def update(self, _):
        # Sincroniza imagem com o estado atual do monstro pai
        self.image = self.frames[self.monster_sprite.state][self.monster_sprite.adjusted_frame_index]
        # Se o monstro pai morrer (sair dos grupos), o contorno morre junto
        if not self.monster_sprite.groups():
            self.kill()

class MonsterNameSprite(pygame.sprite.Sprite):
    """
    Exibe o nome do monstro em uma caixinha acima dele.
    """
    def __init__(self, pos, monster_sprite, groups, font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.z = BATTLE_LAYERS['name']

        text_surf = font.render(monster_sprite.monster.name, False, COLORS['black'])
        padding = 10

        # Cria fundo branco com padding
        self.image = pygame.Surface((text_surf.get_width() + 2 * padding, text_surf.get_height() + 2 * padding)) 
        self.image.fill(COLORS['white'])
        self.image.blit(text_surf, (padding, padding))
        self.rect = self.image.get_frect(midtop = pos)

    def update(self, _):
        if not self.monster_sprite.groups():
            self.kill()

class MonsterLevelSprite(pygame.sprite.Sprite):
    """
    Exibe o nível e a barra de XP (preta fininha).
    """
    def __init__(self, entity, pos, monster_sprite, groups, font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.font = font
        self.z = BATTLE_LAYERS['name']

        self.image = pygame.Surface((60,26))