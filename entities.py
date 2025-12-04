from settings import *
from support import check_connections
from tempo import Tempo
from random import choice
from monster import Monster

class Entity(pygame.sprite.Sprite):
    """
    Classe base para todos os objetos móveis do jogo (Jogador e NPCs).
    Herda de pygame.sprite.Sprite para facilitar o gerenciamento de grupos e desenho.
    """
    def __init__(self, pos, frames, groups, facing_direction):
        super().__init__(groups) # Inicializa o sprite e o adiciona aos grupos passados
        self.z = WORLD_LAYERS['main'] # Define a camada de renderização (ordem de desenho - Z-index)

        # Configuração de Gráficos e Animação
        self.frame_index, self.frames = 0, frames
        self.facing_direction = facing_direction # Direção inicial ('up', 'down', 'left', 'right')

        # Configuração de Movimento
        self.direction = vector() # Vetor (x, y) que define para onde a entidade vai
        self.speed = 250 # Velocidade de movimento em pixels por segundo
        self.blocked = False # Estado que impede o movimento (ex: durante diálogos)

        # Configuração do Sprite e Colisão
        self.image = self.frames[self.get_state()][self.frame_index] # Define a imagem inicial baseada no estado
        self.rect = self.image.get_frect(center = pos) # Cria o retângulo de posição (frect usa float para precisão)
        
        # Cria uma hitbox menor que a imagem para simular profundidade (pés do personagem)
        # inflate reduz a largura pela metade e a altura em 60px
        self.hitbox = self.rect.inflate(-self.rect.width / 2, -60)

        self.y_sort = self.rect.centery # Usado para ordenar o desenho (quem está mais "embaixo" na tela desenha por cima)

    def animate(self, dt):
        # Avança o índice da animação baseado no tempo (dt) e velocidade global
        self.frame_index += ANIMATION_SPEED * dt
        # Atualiza a imagem atual usando o resto da divisão (%) para criar um loop infinito de animação
        self.image = self.frames[self.get_state()][int(self.frame_index % len(self.frames[self.get_state()]))]

    def get_state(self):
        # Verifica se o vetor de direção não é zero (entidade está se movendo)
        moving = bool(self.direction)
        if moving:
            # Define a direção do olhar baseado no movimento X ou Y
            if self.direction.x != 0:
                self.facing_direction = 'right' if self.direction.x > 0 else 'left'
            if self.direction.y != 0:
                self.facing_direction = 'down' if self.direction.y > 0 else 'up'
        
        # Retorna string formatada para buscar a animação correta no dicionário self.frames
        # Exemplo: 'down' (se movendo) ou 'down_idle' (parado)
        return f"{self.facing_direction}{'' if moving else '_idle'}"

    def change_facing_direction(self, target_pos):
        # Calcula o vetor de distância entre a entidade e um alvo
        relation = vector(target_pos) - vector(self.rect.center)
        
        # Se a diferença vertical for pequena (<30), prioriza olhar para os lados
        if abs(relation.y) < 30:
            self.facing_direction = 'right' if relation.x > 0 else 'left'
        else:
            # Caso contrário, olha para cima ou para baixo
            self.facing_direction = 'down' if relation.y > 0 else 'up'

    def block(self):
        # Trava a entidade (usado em cutscenes ou batalhas)
        self.blocked = True
        self.direction = vector(0,0) # Zera a velocidade para parar imediatamente

    def unblock(self):
        # Destrava a entidade
        self.blocked = False

class Character(Entity):
    """
    Classe para NPCs e Inimigos. Possui lógica de visão (Raycast),
    perseguição e inicialização de batalhas.
    """
    def __init__(self, pos, frames, groups, facing_direction, character_data, player, create_dialog, collision_sprites, radius, nurse, notice_sound):
        super().__init__(pos, frames, groups, facing_direction)
        
        # Atributos específicos do NPC
        self.character_data = character_data # Dados do JSON (falas, tipo, monstros)
        self.player = player # Referência ao objeto do jogador para interações
        self.create_dialog = create_dialog # Função callback para criar balões de fala
        # Lista de obstáculos para colisão (exclui o próprio NPC)
        self.collision_rects = [sprite.rect for sprite in collision_sprites if sprite is not self]
        self.nurse = nurse # Booleano indicando se é uma enfermeira (cura)
        
        # Cria os monstros do NPC se existirem no dicionário de dados
        self.monsters = {i: Monster(name, lvl) for i, (name, lvl) in character_data['monsters'].items()} if 'monsters' in character_data else None

        # Flags de Estado
        self.has_moved = False # Se já perseguiu o player
        self.can_rotate = True # Se pode ficar girando aleatoriamente
        self.has_noticed = False # Se notou o player
        self.radius = int(radius) # Raio de visão
        self.view_directions = character_data['directions'] # Direções que ele pode olhar

        # Timers para comportamentos automáticos
        self.timers = {
            'look around': Tempo(1500, autostart = True, repeat = True, func = self.random_view_direction), # Gira a cada 1.5s
            'notice': Tempo(500, func = self.start_move) # Delay de 0.5s após notar o player antes de andar
        }
        self.notice_sound = notice_sound # Efeito sonoro de "Exclamação"

    def random_view_direction(self):
        # Escolhe uma direção aleatória se permitido
        if self.can_rotate:
            self.facing_direction = choice(self.view_directions)

    def get_dialog(self):
        # Retorna o diálogo 'defeated' se já perdeu, ou 'default' se não
        return self.character_data['dialog'][f"{'defeated' if self.character_data['defeated'] else 'default'}"]

    def raycast(self):
        # Lógica de detecção do jogador ("Linha de Visão")
        
        # Proteção: Se o objeto player não existe, aborta para não travar o jogo
        if not self.player:
            return
        
        # Condições para notar o jogador:
        # 1. check_connections: Verifica se o jogador está na frente do NPC e no raio correto
        # 2. has_los: Verifica se não tem paredes no caminho
        # 3. Flags: Não se moveu, não notou ainda
        if check_connections(self.radius, self, self.player) and self.has_los() and not self.has_moved and not self.has_noticed:
            self.player.block() # Trava o jogador
            self.player.change_facing_direction(self.rect.center) # O jogador olha para o NPC
            self.timers['notice'].activate() # Inicia o timer para começar a andar
            self.can_rotate = False # NPC para de girar
            self.has_noticed = True # Marca que notou
            self.player.noticed = True # Avisa o jogador que ele foi notado (pode mostrar ícone)
            self.notice_sound.play() # Toca som

    def has_los(self):
        # Verifica "Line of Sight" (Linha de Visão) checando colisões com paredes
        if vector(self.rect.center).distance_to(self.player.rect.center) < self.radius:
            # Cria uma linha imaginária entre NPC e Player e vê se ela cruza algum obstáculo
            collisions = [bool(rect.clipline(self.rect.center, self.player.rect.center)) for rect in self.collision_rects]
            # Retorna True apenas se NÃO houver colisões no caminho
            return not any(collisions)

    def start_move(self):
        # Calcula vetor normalizado apontando para o jogador para iniciar perseguição
        relation = (vector(self.player.rect.center) - vector(self.rect.center)).normalize()
        self.direction = vector(round(relation.x), round(relation.y))

    def move(self, dt):
        # Lógica de movimento específica do NPC perseguidor
        if not self.has_moved and self.direction:
            # Se a hitbox expandida não encosta no jogador, continua andando
            if not self.hitbox.inflate(10,10).colliderect(self.player.hitbox):
                self.rect.center += self.direction * self.speed * dt
                self.hitbox.center = self.rect.center
            else:
                # Se encostou: para, marca como movido, inicia diálogo e libera o estado de "notado" do player
                self.direction = vector()
                self.has_moved = True
                self.create_dialog(self)
                self.player.noticed = False

    def update(self, dt):
        # Atualiza timers
        for timer in self.timers.values():
            timer.update()

        # Roda animação
        self.animate(dt)
        
        # Se a flag 'look_around' for True no JSON, executa a lógica de visão e movimento
        if self.character_data['look_around']:
            self.raycast()
            self.move(dt)

class Player(Entity):
    """
    Classe do Jogador controlável. Lida com Input do teclado e colisão física.
    """
    def __init__(self, pos, frames, groups, facing_direction, collision_sprites):
        super().__init__(pos, frames, groups, facing_direction)
        self.collision_sprites = collision_sprites # Grupo de sprites que são obstáculos (árvores, paredes)
        self.noticed = False # Estado visual para quando um NPC te vê (exclamação na cabeça)

    def input(self):
        # Captura o estado de todas as teclas
        keys = pygame.key.get_pressed()
        input_vector = vector()
        
        # Define o vetor baseado nas setas direcionais
        if keys[pygame.K_UP]:
            input_vector.y -= 1
        if keys[pygame.K_DOWN]:
            input_vector.y += 1
        if keys[pygame.K_LEFT]:
            input_vector.x -= 1
        if keys[pygame.K_RIGHT]:
            input_vector.x += 1
            
        # Normaliza o vetor para que andar na diagonal não seja mais rápido que em linha reta
        self.direction = input_vector.normalize() if input_vector else input_vector

    def move(self, dt):
        # Movimento Eixo X
        self.rect.centerx += self.direction.x * self.speed * dt
        self.hitbox.centerx = self.rect.centerx # Atualiza hitbox junto com a imagem
        self.collisions('horizontal') # Checa e resolve colisão horizontal

        # Movimento Eixo Y
        self.rect.centery += self.direction.y * self.speed * dt
        self.hitbox.centery = self.rect.centery # Atualiza hitbox junto com a imagem
        self.collisions('vertical') # Checa e resolve colisão vertical

    def collisions(self, axis):
        # Verifica colisão contra todos os obstáculos
        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if axis == 'horizontal':
                    # Se estava indo para a direita e bateu, encosta o lado direito da hitbox no lado esquerdo do obstáculo
                    if self.direction.x > 0: 
                        self.hitbox.right = sprite.hitbox.left
                    # Se estava indo para a esquerda e bateu, encosta o lado esquerdo da hitbox no lado direito do obstáculo
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right