from settings import * # Importa configurações globais (cores, camadas, etc.)
from tempo import Tempo # Importa uma classe personalizada de temporizador

class DialogTree:
    """
    Classe Gerenciadora (Lógica): Controla o fluxo da conversa, qual frase
    está sendo exibida e detecta quando o jogador quer avançar o texto.
    """
    def __init__(self, character, player, all_sprites, font, end_dialog):
        self.player = player
        self.character = character
        self.font = font 
        self.all_sprites = all_sprites
        self.end_dialog = end_dialog # Função callback para executar quando o diálogo acabar
        
        # Obtém a lista de textos/strings do objeto personagem
        self.dialog = character.get_dialog()
        self.dialog_num = len(self.dialog) # Número total de frases
        self.dialog_index = 0 # Começa na primeira frase (índice 0)

        # Cria o primeiro balão de fala visualmente na tela
        self.current_dialog = DialogSprite(self.dialog[self.dialog_index], self.character, self.all_sprites, self.font)
        
        # Inicia um timer de 500ms para evitar pular diálogos acidentalmente (cooldown)
        self.dialog_timer = Tempo(500, autostart = True)

    def input(self):
        # Verifica quais teclas foram pressionadas APENAS neste frame (evita segurar tecla)
        keys = pygame.key.get_just_pressed()
        
        # Se apertou ESPAÇO e o timer de espera não está ativo
        if keys[pygame.K_SPACE] and not self.dialog_timer.active:
            # Remove o balão de fala atual da memória/tela
            self.current_dialog.kill()
            # Avança para o próximo índice de diálogo
            self.dialog_index += 1
            
            # Se ainda existirem frases na lista...
            if self.dialog_index < self.dialog_num:
                # Cria um novo balão com a nova frase
                self.current_dialog = DialogSprite(self.dialog[self.dialog_index], self.character, self.all_sprites, self.font)
                # Reativa o timer para dar um intervalo antes de permitir pular novamente
                self.dialog_timer.activate()
            else:
                # Se não há mais frases, chama a função de encerramento
                self.end_dialog(self.character)

    def update(self):
        # Atualiza o timer (contagem de tempo)
        self.dialog_timer.update()
        # Verifica se o jogador apertou algo
        self.input()

class DialogSprite(pygame.sprite.Sprite):
    """
    Classe Visual (Sprite): Cria a imagem do balão de fala, desenha o fundo
    arredondado e o posiciona acima da cabeça do personagem.
    """
    def __init__(self, message, character, groups, font):
        super().__init__(groups) # Inicializa a herança de Sprite do Pygame
        self.z = WORLD_LAYERS['top'] # Garante que o balão seja desenhado na camada superior

        # Renderiza o texto (transforma a string em uma imagem/superfície)
        text_surf = font.render(message, False, COLORS['black'])
        
        padding = 5 # Margem interna entre o texto e a borda do balão
        # Calcula a largura do balão (mínimo de 30px ou largura do texto + padding)
        width = max(30, text_surf.get_width() + padding * 2)
        # Calcula a altura baseada no texto + padding
        height = text_surf.get_height() + padding * 2

        # Cria uma superfície vazia que suporta transparência (SRCALPHA)
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((0,0,0,0)) # Preenche com 100% transparente inicialmente
        
        # Desenha um retângulo branco com cantos arredondados na superfície transparente
        # O último argumento '4' define o raio da curvatura dos cantos
        pygame.draw.rect(surf, COLORS['pure white'], surf.get_frect(topleft = (0,0)), 0, 4)
        
        # "Cola" (blit) a imagem do texto exatamente no centro do balão branco
        surf.blit(text_surf, text_surf.get_frect(center = (width / 2, height / 2)))

        self.image = surf # Define a imagem final do sprite
        
        # Posiciona o balão (self.rect) em relação ao personagem
        # midbottom do balão = midtop do personagem + vetor(0, -10)
        # O vetor(0, -10) move o balão 10 pixels para cima para não grudar na cabeça
        self.rect = self.image.get_frect(midbottom = character.rect.midtop + vector(0,-10))