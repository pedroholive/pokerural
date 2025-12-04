import pygame  # Importa a biblioteca Pygame para que possamos usar suas funcionalidades

# Inicializa todos os módulos do Pygame (necessário para fontes, sons, etc.)
pygame.init()

# Cria um objeto de fonte.
# 'None' usa a fonte padrão do sistema. '30' é o tamanho da fonte.
font = pygame.font.Font(None, 30)

def debug(info, y=10, x=10):
    """
    Função para exibir informações de debug na tela.
    info: O valor que você quer mostrar (pode ser texto, número, etc.)
    y: A posição vertical (padrão é 10 pixels do topo)
    x: A posição horizontal (padrão é 10 pixels da esquerda)
    """
    
    # Obtém a superfície atual da tela (a janela do jogo que já foi criada)
    display_surface = pygame.display.get_surface()
    
    # Cria uma superfície de texto (uma imagem com o texto escrito).
    # str(info): Converte a informação para string para evitar erros.
    # True: Ativa o Anti-aliasing (deixa as bordas da letra mais suaves).
    # 'White': A cor do texto.
    debug_surf = font.render(str(info), True, 'White')
    
    # Obtém o retângulo (hitbox) da superfície de texto para posicionamento.
    # topleft=(x, y): Define que o canto superior esquerdo do texto ficará nas coordenadas x, y.
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    
    # Desenha um retângulo preto atrás do texto.
    # Isso garante que o texto seja legível mesmo se o fundo do jogo for branco ou colorido.
    pygame.draw.rect(display_surface, 'Black', debug_rect)
    
    # 'Blita' (desenha) a superfície de texto na superfície principal da tela
    # usando a posição definida no debug_rect.
    display_surface.blit(debug_surf, debug_rect)
